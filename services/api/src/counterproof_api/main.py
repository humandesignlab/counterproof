"""FastAPI application entrypoint.

Thin by design: validate input, call the engine, return the challenge report. The
demo uses the deterministic extractor so it runs without an API key. Documents are
untrusted input: count and size are capped and the text is never executed.

Public-deploy hardening (proportionate, not enterprise theater): the endpoint is
unauthenticated and public, so it carries a request body-size cap and a modest
in-memory per-IP rate limit. These are defense in depth on top of the existing
per-field caps. CORS is hygiene, not defense: anyone can call the API directly, so
the real mitigations are the size caps, the platform request timeout, and the rate
limit. Nothing is persisted and no request bodies are logged.
"""

import os
import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.requests import Request
from starlette.responses import Response

from counterproof_core import __version__ as engine_version
from counterproof_core.extract import (
    DETERMINISTIC_MODEL_VERSION,
    DETERMINISTIC_PROMPT_VERSION,
    DeterministicExtractor,
    PaystubExtraction,
)
from counterproof_core.ingest import Document, load_document
from counterproof_core.report import ChallengeReport, build_report

from . import __version__ as api_version

MAX_DOCUMENTS = 10
MAX_TEXT_CHARS = 100_000
DEFAULT_MAX_BODY_BYTES = 1_000_000
DEFAULT_RATE_LIMIT_PER_MIN = 60


class _RateLimiter:
    """In-memory fixed-window per-key limiter.

    Suitable for a single free-tier instance. It is intentionally not distributed;
    if this ever scales past one instance, replace it with a shared store.
    """

    def __init__(self, limit_per_min: int) -> None:
        self.limit = limit_per_min
        self._hits: dict[str, tuple[int, int]] = {}

    def reset(self) -> None:
        self._hits.clear()

    def allow(self, key: str, now: float) -> bool:
        window = int(now // 60)
        start, count = self._hits.get(key, (window, 0))
        if start != window:
            self._hits[key] = (window, 1)
            return True
        if count >= self.limit:
            return False
        self._hits[key] = (window, count + 1)
        return True


_max_body_bytes = int(os.environ.get("COUNTERPROOF_MAX_BODY_BYTES", DEFAULT_MAX_BODY_BYTES))
_rate_limiter = _RateLimiter(
    int(os.environ.get("COUNTERPROOF_RATE_LIMIT_PER_MIN", DEFAULT_RATE_LIMIT_PER_MIN))
)

app = FastAPI(
    title="Counterproof API",
    version=api_version,
    description="Independent effective-challenge layer for AI underwriting.",
)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def _guard_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            if int(content_length) > _max_body_bytes:
                return JSONResponse({"detail": "request body too large"}, status_code=413)
        except ValueError:
            pass
    if not _rate_limiter.allow(_client_ip(request), time.time()):
        return JSONResponse({"detail": "rate limit exceeded"}, status_code=429)
    return await call_next(request)


app.middleware("http")(_guard_middleware)


# CORS is added last so it is the outermost layer and its headers apply to every
# response, including the 413/429 short-circuits above. Preflight OPTIONS is
# handled here and never reaches the rate limiter.
_default_origins = "http://localhost:3000,http://127.0.0.1:3000"
_web_origins = [
    origin.strip()
    for origin in os.environ.get("COUNTERPROOF_WEB_ORIGIN", _default_origins).split(",")
    if origin.strip()
]
_web_origin_regex = os.environ.get("COUNTERPROOF_WEB_ORIGIN_REGEX") or None
app.add_middleware(
    CORSMiddleware,
    allow_origins=_web_origins,
    allow_origin_regex=_web_origin_regex,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class HealthResponse(BaseModel):
    status: str
    api_version: str
    engine_version: str


class DocumentInput(BaseModel):
    document_id: str = Field(min_length=1, max_length=200)
    text: str = Field(min_length=1, max_length=MAX_TEXT_CHARS)


class VerifyRequest(BaseModel):
    documents: list[DocumentInput] = Field(min_length=1, max_length=MAX_DOCUMENTS)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        api_version=api_version,
        engine_version=engine_version,
    )


@app.post("/verify", response_model=ChallengeReport)
def verify(request: VerifyRequest) -> ChallengeReport:
    extractor = DeterministicExtractor()
    pairs: list[tuple[Document, PaystubExtraction]] = []
    for item in request.documents:
        document = load_document(item.document_id, item.text)
        pairs.append((document, extractor.extract(document)))
    return build_report(
        pairs,
        model_version=DETERMINISTIC_MODEL_VERSION,
        prompt_version=DETERMINISTIC_PROMPT_VERSION,
    )
