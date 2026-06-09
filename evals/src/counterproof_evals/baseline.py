"""Naive single-pass baseline.

A deliberately naive reviewer that reads each field once and, if the expected
fields are present and grounded, calls it good. It does no cross-validation, so it
waves through a paystub whose per-period gross has been inflated but whose YTD
totals were left untouched. It exists only to make the contrast concrete: the
naive read misses the tamper that Counterproof catches.

This is a baseline for the proof, not a product path.
"""

from __future__ import annotations

from counterproof_core.extract import DeterministicExtractor, PaystubExtraction
from counterproof_core.ingest import Document
from counterproof_core.report import RecommendedAction

_REQUIRED_FIELDS = (
    "employee_name",
    "employer_name",
    "pay_frequency",
    "pay_period_start",
    "pay_period_end",
    "pay_date",
    "gross_pay",
    "net_pay",
)


def naive_recommended_action(document: Document) -> RecommendedAction:
    """Pass when the required fields are present and grounded; otherwise review.

    No reconciliation, so an internally inconsistent (tampered) document still
    passes as long as the fields are there.
    """
    extraction: PaystubExtraction = DeterministicExtractor().extract(document)
    for name in _REQUIRED_FIELDS:
        field = getattr(extraction, name)
        if not field.grounded:
            return "review"
    return "pass"
