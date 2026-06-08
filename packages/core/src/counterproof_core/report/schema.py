"""Challenge report schema (see docs/ENGINE.md).

The report is the SR 11-7 effective-challenge artifact: what was checked, what was
found, the evidence, the confidence, and the recommended action, with versions and
input hashes for reproducibility. It records evidence and a recommendation; a
human makes the decision.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from ..citations import Citation

Classification = Literal[
    "match",
    "minor_variance",
    "material_discrepancy",
    "missing",
    "contradiction",
    "unverified",
]
Severity = Literal["info", "review", "block"]
RecommendedAction = Literal["pass", "review", "block"]
CheckStatus = Literal["pass", "variance_within_tolerance", "fail"]


class Finding(BaseModel):
    field: str
    independent_value: Any = None
    primary_value: Any = None
    citations: list[Citation] = Field(default_factory=list)
    confidence: float
    classification: Classification
    severity: Severity
    rationale: str


class CheckResult(BaseModel):
    name: str
    status: CheckStatus
    detail: str = ""
    citations: list[Citation] = Field(default_factory=list)


class AuditEvent(BaseModel):
    step: str
    input_sha256: str
    output_sha256: str
    detail: str = ""


class ChallengeReport(BaseModel):
    document_ids: list[str]
    findings: list[Finding] = Field(default_factory=list)
    checks: list[CheckResult] = Field(default_factory=list)
    overall_confidence: float
    recommended_action: RecommendedAction
    audit_trail: list[AuditEvent] = Field(default_factory=list)
    engine_version: str
    model_version: str
    prompt_version: str
    policy_version: str
