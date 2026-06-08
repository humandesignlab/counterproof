"""Cross-validation and disagreement-detection stage.

Checks internal and cross-document consistency, and when a primary system's
output is supplied, classifies each field as match, minor variance, material
discrepancy, missing, or contradiction.

v1 implements the within-paystub YTD-vs-per-period consistency check. Cross-
document checks and disagreement detection against a primary system land later.
"""

from .checks import YTD_CHECK_NAME, run_checks, ytd_consistency_check

__all__ = [
    "YTD_CHECK_NAME",
    "run_checks",
    "ytd_consistency_check",
]
