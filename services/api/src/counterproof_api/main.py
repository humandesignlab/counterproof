"""FastAPI application entrypoint.

Thin by design: validate input, call the engine, return the challenge report. The
demo uses the deterministic extractor so it runs without an API key. Documents are
untrusted input: count and size are capped and the text is never executed.
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

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

app = FastAPI(
    title="Counterproof API",
    version=api_version,
    description="Independent effective-challenge layer for AI underwriting.",
)

_web_origin = os.environ.get("COUNTERPROOF_WEB_ORIGIN", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[_web_origin],
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
