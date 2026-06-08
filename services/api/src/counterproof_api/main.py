"""FastAPI application entrypoint.

Thin by design. Task 1 exposes only a health check so the service builds and is
testable end to end. Engine wiring lands in a later slice.
"""

from fastapi import FastAPI
from pydantic import BaseModel

from counterproof_core import __version__ as engine_version

from . import __version__ as api_version

app = FastAPI(
    title="Counterproof API",
    version=api_version,
    description="Independent effective-challenge layer for AI underwriting.",
)


class HealthResponse(BaseModel):
    status: str
    api_version: str
    engine_version: str


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        api_version=api_version,
        engine_version=engine_version,
    )
