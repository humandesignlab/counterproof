# Counterproof

**The independent effective-challenge layer for AI underwriting.**

Counterproof is an open-core verification layer that runs alongside any AI underwriting pipeline and gives you a transparent second opinion. It independently re-derives the figures that drive a lending decision, grounds each one in a citation, cross-checks the documents against each other, flags where it disagrees with the primary system, and produces an auditable challenge report. It never makes the decision. A human underwriter stays accountable.

<!-- badges: license, CI status, PyPI/npm. Add once the scaffold and CI exist. -->

## Why this exists

An AI underwriting system that validates its own inputs forms a closed loop that cannot catch its own errors or fraud. The industry calls this Verification Collapse. US model-risk guidance (SR 11-7) addresses it head on: it requires "effective challenge," an independent, critical review of a model's outputs, and it applies to vendor models too, not just in-house ones.

Counterproof is that challenge, as code: an independent reader that checks the primary system's work and documents what it finds.

## See it work

<!-- Replace with a short GIF of the demo once built. -->

Feed in a clean document set and Counterproof passes it. Plant a discrepancy, an altered income figure, or a paystub that does not reconcile with the bank deposits, and Counterproof catches it, flags it, and cites the exact location, while a naive single-pass read waves it through. That before-and-after is the whole point.

## What it does

- Independently re-extracts the key underwriting figures from source documents, each with a citation back to its location.
- Cross-validates figures against each other and across documents (income versus deposits, stated versus computed DTI, identity and dates).
- Detects and classifies disagreements with the primary system's output: match, minor variance, material discrepancy, missing, or contradiction.
- Scores confidence and applies an explicit, versioned escalation policy.
- Treats every document as untrusted input, with prompt-injection and PII awareness.
- Emits an auditable challenge report that doubles as SR 11-7 effective-challenge documentation.

## Who it's for

Engineers and teams building or operating AI underwriting in lending and fintech, and the risk and compliance functions that have to validate it.

## Quickstart

Counterproof is a monorepo: a Python verification engine and FastAPI service, plus a Next.js demo UI. The demo runs on synthetic data only and needs no API key.

### Prerequisites

- Python 3.12+ and [uv](https://docs.astral.sh/uv/) (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Node.js 20+ and pnpm (`corepack enable`)
- git

### 1. Clone and install

```bash
git clone https://github.com/humandesignlab/counterproof.git
cd counterproof
uv sync         # Python workspace: engine, API, evals, synthetic data
pnpm install    # JS workspace: the demo UI
```

### 2. Run the demo (two terminals, from the repo root)

Terminal 1, the API:

```bash
uv run uvicorn counterproof_api.main:app --port 8000
```

Terminal 2, the web UI:

```bash
pnpm --filter @counterproof/web dev
```

Open http://localhost:3000. Click "Load tampered sample", then "Run Counterproof": a naive single-pass read passes it, while Counterproof flags it for review and cites the exact line where the per-period income stops reconciling with the year-to-date totals. "Load clean sample" passes both. That before-and-after is the whole point.

The UI calls the API at `http://localhost:8000` by default. To point it elsewhere, set `NEXT_PUBLIC_API_URL` before `pnpm ... dev`.

### 3. Run the engine and evals (no UI)

```bash
uv run python -m counterproof_evals   # score the golden + adversarial sets against thresholds
uv run pytest                         # full test suite (engine, API, evals)
```

Generate a synthetic set to inspect (synthetic data only, never real PII):

```bash
uv run python -m counterproof_synthetic --out generated/demo --count 10 --variant mixed --seed 7
```

## How it works

A transparent, reproducible pipeline: ingest, independent extraction, grounding, cross-validation, disagreement detection, confidence and escalation, guardrails, and challenge-report assembly. See [docs/ENGINE.md](docs/ENGINE.md) for the full specification.

## Open core

The core engine, the base pipeline, the synthetic-data generator, and the eval harness are open source. A paid kit adds advanced detectors, larger labeled eval datasets, adapters that diff against named primary systems, an audit-trail export, and a production deployment.

## Non-goals

Counterproof is not a primary extraction engine, not a scoring or decisioning model, not an origination system, and not a substitute for a human underwriter or for legal and compliance sign-off. It produces evidence and documentation. People make the decision.

## Data and safety

Counterproof is built and tested with synthetic documents only, never real PII. The synthetic-data generator and all test fixtures ship in the repo.

## Compliance

In its synthetic, stateless v1 form, Counterproof processes no real personal data, so privacy and financial-data regulations are not triggered by the reference itself. Deploying it against real borrower documents is a different matter and pulls in GLBA, FCRA and ECOA, the EU AI Act, GDPR, and CCPA. See [COMPLIANCE.md](COMPLIANCE.md) for what a real deployment inherits and how Counterproof supports it. None of this is a certification, and none of it is legal advice.

## Status

Early and active.

## License

The open-source core is licensed under the GNU Affero General Public License v3.0 or later (AGPL-3.0-or-later). See [LICENSE](LICENSE).

The paid kit is not covered by this license and ships under a separate commercial license. If the AGPL does not fit your deployment, a commercial license will be available.
