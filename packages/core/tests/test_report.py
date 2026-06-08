from counterproof_core import __version__
from counterproof_core.extract import (
    DETERMINISTIC_MODEL_VERSION,
    DETERMINISTIC_PROMPT_VERSION,
    DeterministicExtractor,
)
from counterproof_core.ingest import load_document
from counterproof_core.report import ChallengeReport, build_report

SAMPLE = """PAYSTUB
Employer: Acme Fixtures LLC
Employee: Jordan Sample
Pay Frequency: biweekly
Pay Period: 2025-01-01 to 2025-01-14
Pay Date: 2025-01-19

Earnings
  Gross Pay (this period): 4200.00
  Deductions (this period): 1000.00
  Net Pay (this period): 3200.00
"""


def _report_from(text: str, document_id: str = "paystub-0001") -> ChallengeReport:
    document = load_document(document_id, text)
    extraction = DeterministicExtractor().extract(document)
    return build_report(
        [(document, extraction)],
        model_version=DETERMINISTIC_MODEL_VERSION,
        prompt_version=DETERMINISTIC_PROMPT_VERSION,
    )


def test_report_from_clean_paystub_is_valid_and_passes() -> None:
    report = _report_from(SAMPLE)

    assert report.document_ids == ["paystub-0001"]
    assert len(report.findings) == 8
    assert report.engine_version == __version__
    assert report.model_version == DETERMINISTIC_MODEL_VERSION
    assert report.policy_version == "escalation-v1"

    for finding in report.findings:
        assert finding.classification == "unverified"
        assert finding.severity == "info"
        assert finding.confidence == 1.0
        assert finding.citations

    assert report.overall_confidence == 1.0
    assert report.recommended_action == "pass"


def test_report_has_audit_trail_with_hashes() -> None:
    report = _report_from(SAMPLE)
    steps = [event.step for event in report.audit_trail]
    assert steps == ["ingest", "extract", "validate", "assemble"]
    for event in report.audit_trail:
        assert len(event.input_sha256) == 64
        assert len(event.output_sha256) == 64
    # The audit trail chains: each step's input is the prior step's output.
    for earlier, later in zip(report.audit_trail[:-1], report.audit_trail[1:], strict=True):
        assert later.input_sha256 == earlier.output_sha256


def test_report_serializes_and_round_trips() -> None:
    report = _report_from(SAMPLE)
    payload = report.model_dump_json()
    restored = ChallengeReport.model_validate_json(payload)
    assert restored.document_ids == report.document_ids
    assert len(restored.findings) == len(report.findings)
    assert restored.recommended_action == report.recommended_action


def test_report_is_deterministic() -> None:
    assert _report_from(SAMPLE).model_dump_json() == _report_from(SAMPLE).model_dump_json()


def test_missing_fields_escalate_to_review() -> None:
    report = _report_from("PAYSTUB\nEmployer: Acme Fixtures LLC\n", "paystub-0002")

    missing = [f for f in report.findings if f.classification == "missing"]
    assert missing
    assert all(f.severity == "review" for f in missing)
    assert report.recommended_action == "review"
