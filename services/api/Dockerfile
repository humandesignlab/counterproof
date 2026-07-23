# Counterproof API image.
#
# Build context is the repo root (the uv workspace), so the engine
# (packages/core) is installed as a normal package alongside the API. Runtime
# dependencies only: no dev tools, no anthropic-free trimming here (that is a
# separate cleanup). Synthetic-only demo; no secrets are baked in.

FROM python:3.12-slim

# uv provides reproducible, locked installs.
COPY --from=ghcr.io/astral-sh/uv:0.7.10 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PORT=8000

WORKDIR /app

COPY . .

# Install the locked runtime closure for the workspace (no dev group).
RUN uv sync --frozen --no-dev

EXPOSE 8000

# Bind to all interfaces on the platform-provided port.
CMD ["sh", "-c", ".venv/bin/uvicorn counterproof_api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
