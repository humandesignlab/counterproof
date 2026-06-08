from datetime import date

from counterproof_core.extract import DeterministicExtractor
from counterproof_core.ingest import load_document

SAMPLE = """PAYSTUB
Employer: Acme Fixtures LLC
Employee: Jordan Sample
Pay Frequency: biweekly
Pay Period: 2025-01-01 to 2025-01-14
Pay Date: 2025-01-19

Earnings
  Gross Pay (this period): 4200.00
  Deductions (this period): 1000.00
  Net Pay (this period): 3200.00

Year to Date
  YTD Gross: 8400.00
  YTD Net: 6400.00
  Annualized Gross: 109200.00
"""


def test_extracts_all_fields_with_citations() -> None:
    document = load_document("paystub-test", SAMPLE)
    result = DeterministicExtractor().extract(document)

    assert result.employer_name.value == "Acme Fixtures LLC"
    assert result.employee_name.value == "Jordan Sample"
    assert result.pay_frequency.value == "biweekly"
    assert result.pay_period_start.value == date(2025, 1, 1)
    assert result.pay_period_end.value == date(2025, 1, 14)
    assert result.pay_date.value == date(2025, 1, 19)
    assert result.gross_pay.value == 4200.00
    assert result.net_pay.value == 3200.00

    fields = [
        result.employer_name,
        result.employee_name,
        result.pay_frequency,
        result.pay_period_start,
        result.pay_period_end,
        result.pay_date,
        result.gross_pay,
        result.net_pay,
    ]
    for field in fields:
        assert field.grounded
        assert field.confidence == 1.0
        assert field.citations
        assert field.citations[0].document_id == "paystub-test"
        assert field.citations[0].location.startswith("line ")


def test_citation_points_to_the_source_line() -> None:
    document = load_document("paystub-test", SAMPLE)
    result = DeterministicExtractor().extract(document)
    citation = result.gross_pay.citations[0]
    assert citation.location == "line 9"
    assert "Gross Pay (this period): 4200.00" in citation.snippet


def test_missing_fields_are_ungrounded_not_fabricated() -> None:
    document = load_document("empty", "PAYSTUB\n(no recognizable fields)\n")
    result = DeterministicExtractor().extract(document)

    assert result.gross_pay.value is None
    assert result.gross_pay.grounded is False
    assert result.gross_pay.confidence == 0.0
    assert result.employee_name.value is None
    assert result.pay_date.value is None
