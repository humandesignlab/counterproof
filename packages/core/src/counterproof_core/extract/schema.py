"""Strict schema for independent extraction.

Each field is returned as a typed value with a per-field confidence and zero or
more citations. A field with no citation is ungrounded and treated as low
confidence. Missing values are reported as None, never fabricated.
"""

from __future__ import annotations

from datetime import date
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

from ..citations import Citation

T = TypeVar("T")

UNGROUNDED_CONFIDENCE = 0.0
GROUNDED_CONFIDENCE = 1.0


class ExtractedField(BaseModel, Generic[T]):
    value: T | None = None
    confidence: float = UNGROUNDED_CONFIDENCE
    citations: list[Citation] = Field(default_factory=list)

    @property
    def grounded(self) -> bool:
        return self.value is not None and len(self.citations) > 0


class PaystubExtraction(BaseModel):
    """The v1 underwriting-relevant field set re-derived from a paystub."""

    employee_name: ExtractedField[str] = Field(default_factory=ExtractedField[str])
    employer_name: ExtractedField[str] = Field(default_factory=ExtractedField[str])
    pay_frequency: ExtractedField[str] = Field(default_factory=ExtractedField[str])
    pay_period_start: ExtractedField[date] = Field(default_factory=ExtractedField[date])
    pay_period_end: ExtractedField[date] = Field(default_factory=ExtractedField[date])
    pay_date: ExtractedField[date] = Field(default_factory=ExtractedField[date])
    gross_pay: ExtractedField[float] = Field(default_factory=ExtractedField[float])
    net_pay: ExtractedField[float] = Field(default_factory=ExtractedField[float])
