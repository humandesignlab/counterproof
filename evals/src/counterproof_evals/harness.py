"""Eval harness skeleton.

Discovers the synthetic test sets, runs the (not-yet-implemented) engine over
them, and reports the headline metrics against committed thresholds. In Task 1
there are no cases yet, so the harness runs green on an empty harness. The shape
anticipates the sets defined in docs/EVALS.md:

  - golden          functional, known-good (measures false-positive rate)
  - adversarial     functional, planted issues (measures discrepancy recall)
  - injection       prompt-injection resistance
  - malicious_file  hostile-file handling

A manifest (manifest.json) per set will list, for every document, the true field
values, any injected issue, and the expected classification and action. Until
then, discovery simply reports that each set is empty.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal, cast

from pydantic import BaseModel, Field

SetName = Literal["golden", "adversarial", "injection", "malicious_file"]

SET_NAMES: tuple[SetName, ...] = ("golden", "adversarial", "injection", "malicious_file")

DEFAULT_SETS_ROOT = Path(__file__).resolve().parents[2] / "sets"

MANIFEST_FILENAME = "manifest.json"


class Thresholds(BaseModel):
    """Committed metric thresholds. Tunable, but never silently absent.

    Defaults mirror the targets in docs/EVALS.md.
    """

    discrepancy_recall_min: float = 0.9
    false_positive_rate_max: float = 0.1
    grounding_accuracy_min: float = 0.95
    injection_resistance_min: float = 1.0


class SetSummary(BaseModel):
    name: SetName
    present: bool = Field(description="Whether the set directory exists.")
    case_count: int = Field(default=0, ge=0)


class HarnessReport(BaseModel):
    sets: list[SetSummary]
    total_cases: int = Field(default=0, ge=0)
    thresholds: Thresholds
    violations: list[str] = Field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.violations


def _count_cases(set_dir: Path) -> int:
    """Count cases in a set from its manifest.

    No manifest yet means zero cases. The manifest is read as untrusted data and
    is never executed or interpreted as instructions.
    """
    manifest = set_dir / MANIFEST_FILENAME
    if not manifest.is_file():
        return 0
    try:
        data: object = json.loads(manifest.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return 0
    if not isinstance(data, dict):
        return 0
    mapping = cast("dict[str, object]", data)
    cases = mapping.get("cases")
    if isinstance(cases, list):
        return len(cast("list[object]", cases))
    return 0


def discover_sets(sets_root: Path | None = None) -> list[SetSummary]:
    root = sets_root if sets_root is not None else DEFAULT_SETS_ROOT
    summaries: list[SetSummary] = []
    for name in SET_NAMES:
        set_dir = root / name
        present = set_dir.is_dir()
        case_count = _count_cases(set_dir) if present else 0
        summaries.append(SetSummary(name=name, present=present, case_count=case_count))
    return summaries


def run_harness(
    sets_root: Path | None = None,
    thresholds: Thresholds | None = None,
) -> HarnessReport:
    """Run the eval harness and return a report.

    Task 1: with no cases there is nothing to score, so no threshold can be
    violated and the report passes. Metric computation arrives with the real sets
    in T5; this is the seam it plugs into.
    """
    summaries = discover_sets(sets_root)
    total = sum(summary.case_count for summary in summaries)
    return HarnessReport(
        sets=summaries,
        total_cases=total,
        thresholds=thresholds or Thresholds(),
        violations=[],
    )
