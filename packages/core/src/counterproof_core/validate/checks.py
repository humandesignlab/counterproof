"""Cross-validation checks.

v1 implements the within-paystub consistency check from docs/ENGINE.md: the
year-to-date gross should be an integer multiple of the per-period gross (constant
pay). A tamper that inflates the per-period figure while leaving YTD untouched
breaks that invariant, which is how the engine catches it. Each check yields
evidence (a CheckResult with citations), not a verdict.
"""

from __future__ import annotations

from ..citations import Citation
from ..extract.schema import PaystubExtraction
from ..report.schema import CheckResult

YTD_RATIO_TOLERANCE = 0.02
YTD_CHECK_NAME = "ytd_vs_per_period"


def ytd_consistency_check(extraction: PaystubExtraction) -> CheckResult | None:
    """Check YTD gross against per-period gross.

    Returns None when the fields needed to evaluate are absent (nothing to assert),
    so a missing value never masquerades as a passed check.
    """
    gross = extraction.gross_pay
    ytd = extraction.ytd_gross
    if gross.value is None or ytd.value is None or gross.value == 0:
        return None

    citations: list[Citation] = [*gross.citations, *ytd.citations]
    ratio = ytd.value / gross.value
    nearest = round(ratio)

    if nearest >= 1 and abs(ratio - nearest) <= YTD_RATIO_TOLERANCE:
        return CheckResult(
            name=YTD_CHECK_NAME,
            status="pass",
            detail=(
                f"YTD gross {ytd.value:.2f} is {nearest}x the per-period gross "
                f"{gross.value:.2f}, consistent with constant pay."
            ),
            citations=citations,
        )

    return CheckResult(
        name=YTD_CHECK_NAME,
        status="fail",
        detail=(
            f"YTD gross {ytd.value:.2f} is not an integer multiple of the per-period "
            f"gross {gross.value:.2f} (ratio {ratio:.3f}); the per-period figure does "
            "not reconcile with year-to-date totals."
        ),
        citations=citations,
    )


def run_checks(extraction: PaystubExtraction) -> list[CheckResult]:
    results: list[CheckResult] = []
    ytd = ytd_consistency_check(extraction)
    if ytd is not None:
        results.append(ytd)
    return results
