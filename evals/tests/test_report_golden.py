"""Golden report eval (Task 4 definition of done).

Generate a clean golden paystub, extract, assemble the ChallengeReport, and
assert it is valid and serializable and recommends pass with no findings flagged
for review. This is the end-to-end seam the killer-demo eval builds on in T6.
"""

from pathlib import Path

from counterproof_core.extract import (
    DETERMINISTIC_MODEL_VERSION,
    DETERMINISTIC_PROMPT_VERSION,
    DeterministicExtractor,
)
from counterproof_core.ingest import load_document_from_path
from counterproof_core.report import ChallengeReport, build_report
from counterproof_synthetic import generate_set


def test_clean_golden_paystub_yields_passing_report(tmp_path: Path) -> None:
    manifest = generate_set(tmp_path, count=1, variant="clean", seed=23)
    case = manifest.cases[0]
    document = load_document_from_path(tmp_path / case.path)
    extraction = DeterministicExtractor().extract(document)

    report = build_report(
        [(document, extraction)],
        model_version=DETERMINISTIC_MODEL_VERSION,
        prompt_version=DETERMINISTIC_PROMPT_VERSION,
    )

    assert report.document_ids == [case.document_id]
    assert report.recommended_action == "pass"
    assert report.overall_confidence == 1.0
    assert all(finding.severity == "info" for finding in report.findings)
    assert report.audit_trail

    # Valid and serializable.
    restored = ChallengeReport.model_validate_json(report.model_dump_json())
    assert restored.recommended_action == "pass"
