# Eval harness

For a verification tool, the evals are the product. This harness is the proof
that Counterproof catches what a naive single-pass read misses, and it is the CI
regression gate that lets prompts and code change safely.

Synthetic data only. Never commit or test against real financial documents or
real PII.

## Test sets

The harness generates the golden and adversarial sets on the fly from the seeded
`counterproof_synthetic` generator, so nothing is committed and the same seed
reproduces the same sets. Each generated set carries a `manifest.json` listing,
per document, the true field values, any injected issue, and the expected
classification and recommended action.

- golden: clean, known-good. Measures the false-positive rate.
- adversarial: planted issues (currently altered income; more defect types land
  later). Measures discrepancy-detection recall.
- `sets/injection/` and `sets/malicious_file/`: laid out but not scored yet,
  reported as pending so an empty set never looks like a pass. The injection set
  will carry embedded prompt-injection text the engine must treat as data; the
  malicious-file set will carry hostile files the engine must reject or handle
  safely with no crash, hang, resource exhaustion, or external fetch.

## Metrics and thresholds

- discrepancy recall (adversarial flagged / total): min 0.9
- false-positive rate (golden flagged / total): max 0.1
- grounding accuracy (cited line actually contains the value): min 0.95

## Running

```bash
uv run python -m counterproof_evals   # metrics summary; exits non-zero on a violated threshold
uv run pytest evals                   # harness tests
```

The eval job runs in CI on every change, so a metric dropping below threshold
fails the build. This is the regression gate that lets prompts and code change
without silently regressing.
