"""Run the eval harness as a CLI: ``python -m counterproof_evals``.

Prints a compact report and exits non-zero if any committed threshold is
violated. On an empty harness it prints the empty summary and exits 0, which is
the Task 1 CI gate.
"""

from __future__ import annotations

import sys

from .harness import run_harness


def main() -> int:
    report = run_harness()
    print(
        f"Counterproof eval harness: {report.total_cases} case(s) "
        f"across {len(report.sets)} set(s)"
    )
    for summary in report.sets:
        state = "present" if summary.present else "missing"
        print(f"  - {summary.name}: {state}, {summary.case_count} case(s)")
    if report.violations:
        print("Threshold violations:")
        for violation in report.violations:
            print(f"  ! {violation}")
        return 1
    print("All committed thresholds satisfied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
