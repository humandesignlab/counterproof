"""Tests for the public-deploy abuse mitigations.

These run in-process against the app. The Dockerfile smoke test in CI/dev covers
the same behavior against the built image.
"""

import pytest
from fastapi.testclient import TestClient

from counterproof_api import main

VALID = {
    "documents": [
        {"document_id": "d", "text": "PAYSTUB\n  Gross Pay (this period): 10.00\n"}
    ]
}


def test_oversized_body_returns_413(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(main, "_max_body_bytes", 50)
    client = TestClient(main.app)
    response = client.post(
        "/verify",
        json={"documents": [{"document_id": "d", "text": "x" * 500}]},
    )
    assert response.status_code == 413


def test_exceeding_the_window_returns_429(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(main._rate_limiter, "limit", 3)
    main._rate_limiter.reset()
    client = TestClient(main.app)
    statuses = [client.post("/verify", json=VALID).status_code for _ in range(4)]
    assert statuses == [200, 200, 200, 429]
    main._rate_limiter.reset()


def test_normal_traffic_is_not_limited(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(main._rate_limiter, "limit", 60)
    main._rate_limiter.reset()
    client = TestClient(main.app)
    for _ in range(5):
        assert client.post("/verify", json=VALID).status_code == 200
    main._rate_limiter.reset()
