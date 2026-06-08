"""Typed schemas for synthetic paystubs and their ground-truth manifest.

The manifest is the source of truth the eval harness scores against: per document
it records the true field values, any injected issue, and the expected
classification and recommended action. Classification and action literals match
docs/ENGINE.md so later stages can be scored directly.
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

PayFrequency = Literal["weekly", "biweekly", "semimonthly", "monthly"]

PERIODS_PER_YEAR: dict[PayFrequency, int] = {
    "weekly": 52,
    "biweekly": 26,
    "semimonthly": 24,
    "monthly": 12,
}

Variant = Literal["clean", "tampered"]
SetVariant = Literal["clean", "tampered", "mixed"]
IssueType = Literal["altered_income"]

Classification = Literal[
    "match",
    "minor_variance",
    "material_discrepancy",
    "missing",
    "contradiction",
    "unverified",
]
RecommendedAction = Literal["pass", "review", "block"]


class PaystubFields(BaseModel):
    """The true, internally consistent values for one paystub.

    Money fields are per pay period unless prefixed ytd_. annualized_gross is the
    derived gross_pay times periods per year.
    """

    employee_name: str
    employer_name: str
    pay_frequency: PayFrequency
    pay_period_start: date
    pay_period_end: date
    pay_date: date
    gross_pay: float
    deductions: float
    net_pay: float
    ytd_gross: float
    ytd_net: float
    annualized_gross: float


class IssueRecord(BaseModel):
    """A labeled, controlled defect planted in a document."""

    type: IssueType
    field: str
    shown_value: float
    true_value: float
    note: str


class DocumentRecord(BaseModel):
    document_id: str
    path: str
    variant: Variant
    fields: PaystubFields
    injected_issue: IssueRecord | None = None
    expected_classification: Classification
    expected_recommended_action: RecommendedAction


class Manifest(BaseModel):
    generator_version: str
    seed: int
    cases: list[DocumentRecord] = Field(default_factory=list)
