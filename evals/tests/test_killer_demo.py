"""The killer-demo eval (Task 6).

The headline proof: on a clean set Counterproof passes; on a set that differs only
by a planted income discrepancy, Counterproof flags it with a correct citation,
while a naive single-pass baseline waves it through. That before-and-after is the
whole point.
"""

from pathlib import Path

from counterproof_core.extract import (
    DETERMINISTIC_MODEL_VERSION,
    DETERMINISTIC_PROMPT_VERSION,
    DeterministicExtractor,
)
from counterproof_core.ingest import load_document_from_path
from counterproof_core.report import ChallengeReport, build_report
from counterproof_core.validate import YTD_CHECK_NAME
from counterproof_evals import naive_recommended_action
from counterproof_synthetic import generate_set


def _report(document_path: Path) -> ChallengeReport:
    document = load_document_from_path(document_path)
    extraction = DeterministicExtractor().extract(document)
    return build_report(
        [(document, extraction)],
        model_version=DETERMINISTIC_MODEL_VERSION,
        prompt_version=DETERMINISTIC_PROMPT_VERSION,
    )


def test_killer_demo_clean_passes_tampered_is_caught_baseline_misses(tmp_path: Path) -> None:
    clean_dir = tmp_path / "clean"
    tampered_dir = tmp_path / "tampered"
    generate_set(clean_dir, count=1, variant="clean", seed=101)
    generate_set(tampered_dir, count=1, variant="tampered", seed=101)

    clean_path = clean_dir / "paystub-0001.txt"
    tampered_path = tampered_dir / "paystub-0001.txt"

    # Counterproof: clean passes, tampered is flagged.
    clean_report = _report(clean_path)
    tampered_report = _report(tampered_path)
    assert clean_report.recommended_action == "pass"
    assert tampered_report.recommended_action == "review"

    # The flag is grounded: the failed check carries a citation to a real line.
    failed = [check for check in tampered_report.checks if check.status == "fail"]
    assert failed and failed[0].name == YTD_CHECK_NAME
    citation = failed[0].citations[0]
    document_text = tampered_path.read_text(encoding="utf-8")
    cited_line_index = int(citation.location.split()[-1]) - 1
    assert citation.snippet == document_text.splitlines()[cited_line_index].strip()

    # The naive single-pass baseline misses the tamper.
    clean_document = load_document_from_path(clean_path)
    tampered_document = load_document_from_path(tampered_path)
    assert naive_recommended_action(clean_document) == "pass"
    assert naive_recommended_action(tampered_document) == "pass"
