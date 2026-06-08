"""Confidence scoring and escalation policy.

The policy is data, not hardcoded behavior: thresholds live on a versioned Policy
object and the report records the version. These helpers turn extracted fields and
findings into per-finding classification and severity, an overall confidence, and
a recommended action. This recommends; it never decides.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from ..extract.schema import ExtractedField
from ..report.schema import Classification, Finding, RecommendedAction, Severity


class Policy(BaseModel):
    version: str = "escalation-v1"
    min_field_confidence: float = 0.5


def classify_field(field: ExtractedField[Any]) -> Classification:
    """Standalone extraction (no primary system to compare against yet).

    A grounded value is extracted but not yet challenged, so it is unverified. An
    absent value is missing. Values are never fabricated upstream.
    """
    if field.value is None:
        return "missing"
    return "unverified"


def field_severity(field: ExtractedField[Any], policy: Policy) -> Severity:
    if not field.grounded or field.confidence < policy.min_field_confidence:
        return "review"
    return "info"


def overall_confidence(findings: list[Finding]) -> float:
    if not findings:
        return 0.0
    return round(sum(finding.confidence for finding in findings) / len(findings), 4)


def recommended_action(findings: list[Finding]) -> RecommendedAction:
    severities = {finding.severity for finding in findings}
    if "block" in severities:
        return "block"
    if "review" in severities:
        return "review"
    return "pass"
