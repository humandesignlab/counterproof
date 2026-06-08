"""Golden-manifest extraction eval (Task 3 definition of done).

Generate a clean (golden) paystub set, run the deterministic extractor, and
assert that every value matches ground truth within tolerance and that every
value carries a citation. Full grounding-accuracy metrics and thresholds arrive
with the harness wiring in T5; this asserts the contract.
"""

from pathlib import Path
from typing import Any

from counterproof_core.extract import DeterministicExtractor, ExtractedField, PaystubExtraction
from counterproof_core.ingest import load_document_from_path
from counterproof_synthetic import generate_set

MONEY_TOLERANCE = 0.01


def _all_fields(result: PaystubExtraction) -> list[ExtractedField[Any]]:
    return [
        result.employee_name,
        result.employer_name,
        result.pay_frequency,
        result.pay_period_start,
        result.pay_period_end,
        result.pay_date,
        result.gross_pay,
        result.net_pay,
    ]


def test_deterministic_extraction_matches_golden_manifest(tmp_path: Path) -> None:
    manifest = generate_set(tmp_path, count=8, variant="clean", seed=11)
    extractor = DeterministicExtractor()

    for case in manifest.cases:
        document = load_document_from_path(tmp_path / case.path)
        result = extractor.extract(document)

        for field in _all_fields(result):
            assert field.grounded
            assert field.citations

        truth = case.fields
        assert result.employee_name.value == truth.employee_name
        assert result.employer_name.value == truth.employer_name
        assert result.pay_frequency.value == truth.pay_frequency
        assert result.pay_period_start.value == truth.pay_period_start
        assert result.pay_period_end.value == truth.pay_period_end
        assert result.pay_date.value == truth.pay_date

        assert result.gross_pay.value is not None
        assert abs(result.gross_pay.value - truth.gross_pay) <= MONEY_TOLERANCE
        assert result.net_pay.value is not None
        assert abs(result.net_pay.value - truth.net_pay) <= MONEY_TOLERANCE
