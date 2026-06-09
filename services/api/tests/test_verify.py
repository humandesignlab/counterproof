from fastapi.testclient import TestClient

from counterproof_api.main import MAX_TEXT_CHARS, app

client = TestClient(app)

CLEAN = """PAYSTUB
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
"""

TAMPERED = CLEAN.replace(
    "Gross Pay (this period): 4200.00", "Gross Pay (this period): 5600.00"
)


def _verify(document_id: str, text: str):
    return client.post("/verify", json={"documents": [{"document_id": document_id, "text": text}]})


def test_verify_clean_paystub_passes() -> None:
    response = _verify("paystub-clean", CLEAN)
    assert response.status_code == 200
    report = response.json()
    assert report["recommended_action"] == "pass"
    assert report["document_ids"] == ["paystub-clean"]


def test_verify_tampered_paystub_is_flagged_with_a_check() -> None:
    response = _verify("paystub-tampered", TAMPERED)
    assert response.status_code == 200
    report = response.json()
    assert report["recommended_action"] == "review"
    assert any(check["status"] == "fail" for check in report["checks"])


def test_verify_rejects_empty_document_list() -> None:
    response = client.post("/verify", json={"documents": []})
    assert response.status_code == 422


def test_verify_rejects_oversized_text() -> None:
    response = _verify("too-big", "x" * (MAX_TEXT_CHARS + 1))
    assert response.status_code == 422
