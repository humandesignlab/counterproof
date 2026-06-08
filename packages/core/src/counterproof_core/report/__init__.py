"""Challenge report assembly stage.

Produces the structured ChallengeReport plus a human-readable rendering. The
report is the SR 11-7 effective-challenge artifact: what was checked, what was
found, the evidence, the confidence, and the recommended action, with engine,
model, and policy versions and input hashes for reproducibility.

v1 assembles the report from extraction output with a deterministic audit trail.
Cross-validation checks and disagreement detection populate it further later.
"""

from .assemble import build_report
from .schema import (
    AuditEvent,
    ChallengeReport,
    CheckResult,
    Classification,
    Finding,
    RecommendedAction,
    Severity,
)

__all__ = [
    "build_report",
    "AuditEvent",
    "ChallengeReport",
    "CheckResult",
    "Classification",
    "Finding",
    "RecommendedAction",
    "Severity",
]
