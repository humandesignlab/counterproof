"""Run the eval harness as a CLI: ``python -m counterproof_evals``.

Prints a compact report and exits non-zero if any committed threshold is
violated. On an empty harness it prints the empty summary and exits 0, which is
the Task 1 CI gate.
"""

from __future__ import annotations

import sys

from .harness import run_harness


def _format(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def main() -> int:
    report = run_harness()
    metrics = report.metrics
    print("Counterproof eval harness")
    print(f"  golden cases:      {metrics.golden_cases}")
    print(f"  adversarial cases: {metrics.adversarial_cases}")
    print(
        f"  discrepancy recall:   {_format(metrics.discrepancy_recall)} "
        f"(min {report.thresholds.discrepancy_recall_min})"
    )
    print(
        f"  false positive rate:  {_format(metrics.false_positive_rate)} "
        f"(max {report.thresholds.false_positive_rate_max})"
    )
    print(
        f"  grounding accuracy:   {_format(metrics.grounding_accuracy)} "
        f"(min {report.thresholds.grounding_accuracy_min})"
    )
    if report.pending_sets:
        print(f"  pending (not scored): {', '.join(report.pending_sets)}")
    if report.violations:
        print("Threshold violations:")
        for violation in report.violations:
            print(f"  ! {violation}")
        return 1
    print("All committed thresholds satisfied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
