from counterproof_core.extract import (
    DETERMINISTIC_MODEL_VERSION,
    DETERMINISTIC_PROMPT_VERSION,
    DeterministicExtractor,
)
from counterproof_core.ingest import load_document
from counterproof_core.report import build_report
from counterproof_core.validate import YTD_CHECK_NAME, ytd_consistency_check

CLEAN = """PAYSTUB
Employer: Acme Fixtures LLC
Employee: Jordan Sample
Pay Frequency: biweekly
Pay Period: 2025-01-01 to 2025-01-14
Pay Date: 2025-01-19

Earnings
  Gross Pay (this period): 4200.00
  Deductions (this period): 1000.00
  Net Pay (this period): 3200.00

Year to Date
  YTD Gross: 8400.00
  YTD Net: 6400.00
"""

# Per-period gross inflated to 5600.00 while YTD gross stays at the true 8400.00
# (which is 2 x the true 4200.00). 8400 / 5600 = 1.5, not an integer multiple.
TAMPERED = CLEAN.replace("Gross Pay (this period): 4200.00", "Gross Pay (this period): 5600.00")


def _extract(text: str):
    return DeterministicExtractor().extract(load_document("paystub", text))


def test_ytd_check_passes_on_consistent_paystub() -> None:
    result = ytd_consistency_check(_extract(CLEAN))
    assert result is not None
    assert result.status == "pass"
    assert result.citations


def test_ytd_check_fails_when_per_period_does_not_reconcile() -> None:
    result = ytd_consistency_check(_extract(TAMPERED))
    assert result is not None
    assert result.status == "fail"
    assert result.name == YTD_CHECK_NAME


def test_ytd_check_returns_none_without_ytd() -> None:
    text = "PAYSTUB\n  Gross Pay (this period): 4200.00\n"
    assert ytd_consistency_check(_extract(text)) is None


def test_tampered_report_escalates_to_review() -> None:
    document = load_document("paystub-tampered", TAMPERED)
    extraction = DeterministicExtractor().extract(document)
    report = build_report(
        [(document, extraction)],
        model_version=DETERMINISTIC_MODEL_VERSION,
        prompt_version=DETERMINISTIC_PROMPT_VERSION,
    )
    assert report.recommended_action == "review"
    assert any(check.status == "fail" for check in report.checks)
    assert any(finding.classification == "material_discrepancy" for finding in report.findings)


def test_clean_report_passes_with_a_passing_check() -> None:
    document = load_document("paystub-clean", CLEAN)
    extraction = DeterministicExtractor().extract(document)
    report = build_report(
        [(document, extraction)],
        model_version=DETERMINISTIC_MODEL_VERSION,
        prompt_version=DETERMINISTIC_PROMPT_VERSION,
    )
    assert report.recommended_action == "pass"
    assert report.checks
    assert all(check.status == "pass" for check in report.checks)
