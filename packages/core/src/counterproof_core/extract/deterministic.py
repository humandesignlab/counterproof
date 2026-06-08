"""Deterministic extractor.

Re-derives the v1 field set from the fixed, line-based paystub layout, citing the
exact line for every value. Fully reproducible, so it is what CI and the eval
harness score. It also serves as the naive single-pass baseline the killer demo
contrasts against. It re-reads a small set of figures from text; it is not a
primary OCR or extraction engine.
"""

from __future__ import annotations

from datetime import date

from ..citations import Citation
from ..ingest.document import Document
from .schema import (
    GROUNDED_CONFIDENCE,
    UNGROUNDED_CONFIDENCE,
    ExtractedField,
    PaystubExtraction,
)

MODEL_VERSION = "deterministic-extractor-v1"
PROMPT_VERSION = "n/a"


def _citation(document: Document, line_number: int) -> Citation:
    return Citation(
        document_id=document.document_id,
        location=f"line {line_number}",
        snippet=document.line(line_number).strip(),
    )


def _find(document: Document, prefix: str) -> tuple[int, str] | None:
    for line_number, raw_line in enumerate(document.lines, start=1):
        stripped = raw_line.strip()
        if stripped.startswith(prefix):
            return line_number, stripped[len(prefix) :].strip()
    return None


def _str_field(document: Document, prefix: str) -> ExtractedField[str]:
    found = _find(document, prefix)
    if found is None:
        return ExtractedField[str]()
    line_number, value = found
    if not value:
        return ExtractedField[str]()
    return ExtractedField[str](
        value=value,
        confidence=GROUNDED_CONFIDENCE,
        citations=[_citation(document, line_number)],
    )


def _money_field(document: Document, prefix: str) -> ExtractedField[float]:
    found = _find(document, prefix)
    if found is None:
        return ExtractedField[float]()
    line_number, raw = found
    try:
        value = float(raw.replace(",", ""))
    except ValueError:
        return ExtractedField[float](confidence=UNGROUNDED_CONFIDENCE)
    return ExtractedField[float](
        value=value,
        confidence=GROUNDED_CONFIDENCE,
        citations=[_citation(document, line_number)],
    )


def _date_field(document: Document, prefix: str) -> ExtractedField[date]:
    found = _find(document, prefix)
    if found is None:
        return ExtractedField[date]()
    line_number, raw = found
    try:
        value = date.fromisoformat(raw)
    except ValueError:
        return ExtractedField[date]()
    return ExtractedField[date](
        value=value,
        confidence=GROUNDED_CONFIDENCE,
        citations=[_citation(document, line_number)],
    )


def _period_fields(
    document: Document,
) -> tuple[ExtractedField[date], ExtractedField[date]]:
    found = _find(document, "Pay Period:")
    if found is None:
        return ExtractedField[date](), ExtractedField[date]()
    line_number, raw = found
    parts = raw.split(" to ")
    if len(parts) != 2:
        return ExtractedField[date](), ExtractedField[date]()
    try:
        start = date.fromisoformat(parts[0].strip())
        end = date.fromisoformat(parts[1].strip())
    except ValueError:
        return ExtractedField[date](), ExtractedField[date]()
    citation = _citation(document, line_number)
    return (
        ExtractedField[date](value=start, confidence=GROUNDED_CONFIDENCE, citations=[citation]),
        ExtractedField[date](value=end, confidence=GROUNDED_CONFIDENCE, citations=[citation]),
    )


class DeterministicExtractor:
    """Parses the known synthetic paystub layout. Never fabricates a missing value."""

    def extract(self, document: Document) -> PaystubExtraction:
        pay_period_start, pay_period_end = _period_fields(document)
        return PaystubExtraction(
            employee_name=_str_field(document, "Employee:"),
            employer_name=_str_field(document, "Employer:"),
            pay_frequency=_str_field(document, "Pay Frequency:"),
            pay_period_start=pay_period_start,
            pay_period_end=pay_period_end,
            pay_date=_date_field(document, "Pay Date:"),
            gross_pay=_money_field(document, "Gross Pay (this period):"),
            net_pay=_money_field(document, "Net Pay (this period):"),
        )
