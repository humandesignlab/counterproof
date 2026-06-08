# Synthetic data

Synthetic data only. This package never reads, requests, commits, or emits real
PII or real financial documents. That boundary is what keeps the reference
implementation clear of GDPR, CCPA, and GLBA (see `COMPLIANCE.md`).

## Layout

- `src/counterproof_synthetic/` the generator package.
- `generated/` default output location for generated documents and manifests.
  Generated artifacts are not committed.

## Generator

`counterproof_synthetic` produces plaintext paystubs plus a `manifest.json`
ground-truth file. The manifest records, per document, the true field values, any
injected issue, and the expected classification and recommended action, so the
eval harness can score exactly. Documents use a fixed, line-based layout so later
stages can ground each figure in a stable location.

Variants:

- `clean` the document matches the true, reconciled values.
- `tampered` (`altered_income`) the displayed per-period gross and net are
  inflated while year-to-date totals stay true, so the per-period figure no
  longer reconciles with YTD. The manifest still records the true values.
- `mixed` alternates clean and tampered.

The generator is seeded, so the same seed produces an identical set and manifest.

```bash
uv run python -m counterproof_synthetic --out generated/demo --count 10 --variant mixed --seed 7
uv run pytest data/synthetic
```
