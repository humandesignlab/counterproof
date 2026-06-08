# Architecture

## Overview

```
            ┌──────────────────────────────────────────────┐
            │  Documents (synthetic)                        │
            │  paystubs, bank statements, + optional        │
            │  "primary system output" to challenge         │
            └───────────────────────┬──────────────────────┘
                                     │
                    ┌────────────────▼─────────────────┐
                    │  Verification Engine (packages/core)│
                    │  ingest → extract → ground →        │
                    │  cross-validate → disagree →        │
                    │  score → guard → report             │
                    └────────────────┬─────────────────┘
                                     │ Challenge Report (structured)
            ┌────────────────────────▼─────────────────────┐
            │  API (services/api, FastAPI)                  │
            └────────────────────────┬─────────────────────┘
                                     │
            ┌────────────────────────▼─────────────────────┐
            │  Demo UI (apps/web, Next.js)                  │
            │  upload → findings → citations → audit trail  │
            └───────────────────────────────────────────────┘

  Cross-cutting: eval harness (evals/), tracing/logging, synthetic data (data/synthetic/)
```

## Stack

- **Engine:** Python. Claude API via tool use and structured outputs. Pydantic models for every schema. Keep the engine framework-light; a thin orchestration layer over well-typed steps beats a heavy agent framework here.
- **API:** FastAPI. Thin. It validates input, calls the engine, returns the report.
- **UI:** Next.js (App Router) + TypeScript + Tailwind. Demo only in v1: upload, run, render the report with inline citations and the audit trail.
- **Eval harness:** Python, runnable locally and in CI. Treated as a first-class app, not an afterthought.
- **Persistence:** none in v1. Process and return. Add Postgres only when history or accounts are actually needed.

## Repo layout (monorepo)

```
counterproof/
  apps/web/            # Next.js demo UI
  services/api/        # FastAPI service
  packages/core/       # the verification engine (the product)
    ingest/
    extract/
    validate/          # cross-validation + disagreement detection
    score/             # confidence + escalation policy
    guard/             # injection + PII handling
    report/            # challenge report assembly + schema
  evals/               # harness, metrics, test sets
  data/synthetic/      # generator + generated docs + ground-truth manifests
  docs/                # architecture, engine, and other docs
```

## Data flow

1. A document set (and optionally a primary system's output) enters the API.
2. The engine runs its pipeline (see `ENGINE.md`).
3. It returns a structured Challenge Report.
4. The UI renders findings, citations, disagreements, confidence, and the audit trail.

## Open-core boundary

Keep the boundary clean from the first commit so the split is a packaging decision, not a refactor.

- `packages/core` base pipeline, `data/synthetic` generator, `evals` harness, `apps/web` minimal UI: open source.
- Advanced detectors, named-vendor diff adapters, large eval datasets, audit-trail export, production deploy, premium UI: paid kit, kept in clearly separable modules (for example `packages/core/validate/advanced/` and a separate `pro/` directory) so nothing in the OSS core imports from them.

## Key decisions and rationale

- **Re-derive, do not re-OCR.** The value is an independent second read of the figures that drive a decision, with citations, not a better OCR engine.
- **Deterministic and reproducible.** Pin model versions, set temperature low, version the prompts, snapshot inputs. A validation tool that is not reproducible is not credible.
- **Documents are untrusted input.** Every document can contain a prompt-injection payload or planted fraud. The guard layer is not optional.
- **Structured outputs everywhere.** Use tool use and typed schemas so findings are machine-checkable and the eval harness can score them directly.
