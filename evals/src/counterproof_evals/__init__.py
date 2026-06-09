"""Counterproof eval harness.

For a verification tool the evals are the product: they prove the second opinion
catches what the primary system misses, and they are the CI regression gate that
lets prompts and code change safely.

Task 1 ships the harness skeleton and the empty set layout (functional,
injection, malicious-file). Real sets, metrics, and thresholds land in T5.
"""

from .baseline import naive_recommended_action
from .harness import (
    PENDING_SET_NAMES,
    SET_NAMES,
    HarnessReport,
    Metrics,
    Thresholds,
    run_harness,
)

__version__ = "0.1.0"

__all__ = [
    "PENDING_SET_NAMES",
    "SET_NAMES",
    "HarnessReport",
    "Metrics",
    "Thresholds",
    "naive_recommended_action",
    "run_harness",
    "__version__",
]
