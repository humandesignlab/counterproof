"""Eval harness.

Generates seeded golden (clean) and adversarial (tampered) paystub sets, runs the
engine over each case, and scores the headline metrics against committed
thresholds. Seeded generation keeps the harness reproducible and the repo clean:
no fixtures are committed and the same seed yields the same sets.

Scored now: discrepancy recall (adversarial), false-positive rate (golden), and
grounding accuracy. The injection and malicious-file sets are laid out but not yet
scored; they are reported as pending so an empty set never masquerades as a pass.
"""

from __future__ import annotations

import tempfile
from datetime import date
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from counterproof_core.extract import (
    DETERMINISTIC_MODEL_VERSION,
    DETERMINISTIC_PROMPT_VERSION,
    DeterministicExtractor,
    ExtractedField,
    PaystubExtraction,
)
from counterproof_core.ingest import Document, load_document_from_path
from counterproof_core.report import build_report
from counterproof_synthetic import DocumentRecord, generate_set

SetName = Literal["golden", "adversarial", "injection", "malicious_file"]
SET_NAMES: tuple[SetName, ...] = ("golden", "adversarial", "injection", "malicious_file")
PENDING_SET_NAMES: tuple[SetName, ...] = ("injection", "malicious_file")

DEFAULT_SEED = 1
DEFAULT_COUNT = 12


class Thresholds(BaseModel):
    """Committed metric thresholds (see docs/EVALS.md). Tunable, never absent."""

    discrepancy_recall_min: float = 0.9
    false_positive_rate_max: float = 0.1
    grounding_accuracy_min: float = 0.95
    injection_resistance_min: float = 1.0


class Metrics(BaseModel):
    golden_cases: int = 0
    adversarial_cases: int = 0
    discrepancy_recall: float | None = None
    false_positive_rate: float | None = None
    grounding_accuracy: float | None = None


class HarnessReport(BaseModel):
    metrics: Metrics
    thresholds: Thresholds
    pending_sets: list[str] = Field(default_factory=list)
    violations: list[str] = Field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.violations


def _value_text(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.2f}"
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _line_number(location: str) -> int:
    parts = location.split()
    if len(parts) == 2 and parts[0] == "line" and parts[1].isdigit():
        return int(parts[1])
    return 0


def _core_fields(extraction: PaystubExtraction) -> list[ExtractedField[Any]]:
    return [
        extraction.employee_name,
        extraction.employer_name,
        extraction.pay_frequency,
        extraction.pay_period_start,
        extraction.pay_period_end,
        extraction.pay_date,
        extraction.gross_pay,
        extraction.net_pay,
        extraction.ytd_gross,
    ]


def _grounding_score(document: Document, extraction: PaystubExtraction) -> tuple[int, int]:
    """Count grounded fields whose cited line actually contains the value."""
    correct = 0
    total = 0
    for field in _core_fields(extraction):
        if field.value is None or not field.citations:
            continue
        total += 1
        citation = field.citations[0]
        line_text = document.line(_line_number(citation.location))
        if _value_text(field.value) in line_text:
            correct += 1
    return correct, total


def _evaluate_case(
    case: DocumentRecord, set_dir: Path, extractor: DeterministicExtractor
) -> tuple[bool, int, int]:
    document = load_document_from_path(set_dir / case.path)
    extraction = extractor.extract(document)
    report = build_report(
        [(document, extraction)],
        model_version=DETERMINISTIC_MODEL_VERSION,
        prompt_version=DETERMINISTIC_PROMPT_VERSION,
    )
    flagged = report.recommended_action != "pass"
    correct, total = _grounding_score(document, extraction)
    return flagged, correct, total


def _check_thresholds(metrics: Metrics, thresholds: Thresholds) -> list[str]:
    violations: list[str] = []
    recall = metrics.discrepancy_recall
    if recall is not None and recall < thresholds.discrepancy_recall_min:
        violations.append(
            f"discrepancy_recall {recall:.3f} < {thresholds.discrepancy_recall_min}"
        )
    fpr = metrics.false_positive_rate
    if fpr is not None and fpr > thresholds.false_positive_rate_max:
        violations.append(
            f"false_positive_rate {fpr:.3f} > {thresholds.false_positive_rate_max}"
        )
    grounding = metrics.grounding_accuracy
    if grounding is not None and grounding < thresholds.grounding_accuracy_min:
        violations.append(
            f"grounding_accuracy {grounding:.3f} < {thresholds.grounding_accuracy_min}"
        )
    return violations


def _compute_metrics(work_dir: Path, seed: int, count: int) -> Metrics:
    extractor = DeterministicExtractor()

    golden_dir = work_dir / "golden"
    adversarial_dir = work_dir / "adversarial"
    golden = generate_set(golden_dir, count=count, variant="clean", seed=seed)
    adversarial = generate_set(adversarial_dir, count=count, variant="tampered", seed=seed + 1)

    grounded_correct = 0
    grounded_total = 0

    golden_flagged = 0
    for case in golden.cases:
        flagged, correct, total = _evaluate_case(case, golden_dir, extractor)
        golden_flagged += 1 if flagged else 0
        grounded_correct += correct
        grounded_total += total

    adversarial_flagged = 0
    for case in adversarial.cases:
        flagged, correct, total = _evaluate_case(case, adversarial_dir, extractor)
        adversarial_flagged += 1 if flagged else 0
        grounded_correct += correct
        grounded_total += total

    golden_n = len(golden.cases)
    adversarial_n = len(adversarial.cases)
    return Metrics(
        golden_cases=golden_n,
        adversarial_cases=adversarial_n,
        discrepancy_recall=(adversarial_flagged / adversarial_n) if adversarial_n else None,
        false_positive_rate=(golden_flagged / golden_n) if golden_n else None,
        grounding_accuracy=(grounded_correct / grounded_total) if grounded_total else None,
    )


def run_harness(
    *,
    seed: int = DEFAULT_SEED,
    count: int = DEFAULT_COUNT,
    thresholds: Thresholds | None = None,
    work_dir: Path | None = None,
) -> HarnessReport:
    active_thresholds = thresholds or Thresholds()

    if work_dir is not None:
        metrics = _compute_metrics(work_dir, seed, count)
    else:
        with tempfile.TemporaryDirectory(prefix="counterproof-evals-") as tmp:
            metrics = _compute_metrics(Path(tmp), seed, count)

    return HarnessReport(
        metrics=metrics,
        thresholds=active_thresholds,
        pending_sets=list(PENDING_SET_NAMES),
        violations=_check_thresholds(metrics, active_thresholds),
    )
