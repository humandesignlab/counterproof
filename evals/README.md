# Eval harness

For a verification tool, the evals are the product. This harness is the proof
that Counterproof catches what a naive single-pass read misses, and it is the CI
regression gate that lets prompts and code change safely.

Synthetic data only. Never commit or test against real financial documents or
real PII.

## Test sets (`sets/`)

Laid out now, populated in later slices. Each set holds synthetic documents plus
a `manifest.json` listing, per document, the true field values, any injected
issue, and the expected classification and recommended action.

- `golden/` functional, known-good. Measures the false-positive rate.
- `adversarial/` functional, planted issues (altered income, inflated YTD,
  mismatched identity or period, doctored dates, fabricated employer). Measures
  discrepancy-detection recall.
- `injection/` documents with embedded prompt-injection text. The engine must
  treat it as data and still produce a correct, grounded report.
- `malicious_file/` files that are hostile as files (malformed or truncated,
  oversized, decompression bombs, XXE payloads, SSRF bait). The engine must
  reject or safely handle each one with no crash, hang, resource exhaustion, or
  external fetch.

## Running

```bash
uv run python -m counterproof_evals   # CLI summary; exits non-zero on a violated threshold
uv run pytest evals                   # harness unit tests
```

Task 1 ships an empty harness: no cases yet, so it runs green. Real metrics
(recall, false-positive rate, grounding accuracy, injection resistance,
malicious-file handling) and committed thresholds arrive with the sets.
