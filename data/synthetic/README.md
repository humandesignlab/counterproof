# Synthetic data

Synthetic data only. This package never reads, requests, commits, or emits real
PII or real financial documents. That boundary is what keeps the reference
implementation clear of GDPR, CCPA, and GLBA (see `COMPLIANCE.md`).

## Layout

- `src/counterproof_synthetic/` the generator package (skeleton in Task 1).
- `generated/` output location for generated documents and their ground-truth
  manifest. Empty in Task 1.

## Plan

The generator (T2) produces documents plus a ground-truth manifest that records,
per document, the true field values and any injected issue, so the eval harness
can score exactly. It will support a clean variant and a tampered variant
(planted income discrepancy).
