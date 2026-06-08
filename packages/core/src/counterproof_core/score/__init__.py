"""Confidence scoring and escalation stage.

Combines per-field confidence, grounding quality, and check results into an
overall confidence and per-finding severity, then applies an explicit, versioned
escalation policy. The policy is data, not hardcoded. This recommends an action
for a human reviewer; it never makes the underwriting decision.

v1 provides a versioned escalation policy and the confidence and action
aggregation the report consumes. The policy is data, not hardcoded behavior.
"""

from .policy import (
    Policy,
    classify_field,
    field_severity,
    overall_confidence,
    recommended_action,
)

__all__ = [
    "Policy",
    "classify_field",
    "field_severity",
    "overall_confidence",
    "recommended_action",
]
