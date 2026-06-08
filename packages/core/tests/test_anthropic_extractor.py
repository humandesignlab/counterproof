"""Tests for the Anthropic tool-use extractor.

The parsing and type-coercion path is tested deterministically in CI by feeding a
fabricated tool_use block (no network, no key). The live model call is a separate
test that is skipped unless ANTHROPIC_API_KEY is set.
"""

import os
from datetime import date
from pathlib import Path

import pytest
from anthropic.types import ToolUseBlock

from counterproof_core.extract import anthropic as ax
from counterproof_core.ingest import load_document


def _tool_block(payload: dict[str, object], name: str = ax.TOOL_NAME) -> ToolUseBlock:
    return ToolUseBlock(id="block-1", name=name, input=payload, type="tool_use")


def test_parse_and_convert_tool_use_payload() -> None:
    payload: dict[str, object] = {
        "employee_name": {
            "value": "Jordan Sample",
            "line": 3,
            "snippet": "Employee: Jordan Sample",
            "confidence": 0.9,
        },
        "gross_pay": {
            "value": "4,200.00",
            "line": 9,
            "snippet": "Gross Pay (this period): 4200.00",
            "confidence": 0.95,
        },
        "pay_date": {
            "value": "2025-01-19",
            "line": 6,
            "snippet": "Pay Date: 2025-01-19",
            "confidence": 0.8,
        },
        "net_pay": {"value": "N/A", "line": 0, "snippet": "", "confidence": 0.0},
    }
    claims = ax.AnthropicExtractor._parse_claims([_tool_block(payload)])
    document = load_document("paystub-test", "irrelevant for conversion")
    result = ax._to_extraction(document, claims)

    assert result.employee_name.value == "Jordan Sample"
    assert result.employee_name.grounded
    assert result.gross_pay.value == 4200.0
    assert result.gross_pay.citations[0].location == "line 9"
    assert result.pay_date.value == date(2025, 1, 19)

    # net_pay was unparseable and uncited: reported missing, never fabricated.
    assert result.net_pay.value is None
    assert result.net_pay.grounded is False
    assert result.net_pay.confidence == 0.0


def test_uncited_value_is_not_grounded() -> None:
    payload: dict[str, object] = {
        "employer_name": {"value": "Acme", "line": 0, "snippet": "", "confidence": 0.99},
    }
    claims = ax.AnthropicExtractor._parse_claims([_tool_block(payload)])
    result = ax._to_extraction(load_document("d", "x"), claims)
    assert result.employer_name.value == "Acme"
    assert result.employer_name.citations == []
    assert result.employer_name.grounded is False
    assert result.employer_name.confidence == 0.0


def test_parse_raises_when_tool_not_called() -> None:
    block = _tool_block({}, name="some_other_tool")
    with pytest.raises(ValueError):
        ax.AnthropicExtractor._parse_claims([block])


@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="requires ANTHROPIC_API_KEY (live model call)",
)
def test_live_extraction_grounds_fields(tmp_path: Path) -> None:
    from counterproof_core.ingest import load_document_from_path
    from counterproof_synthetic import generate_set

    manifest = generate_set(tmp_path, count=1, variant="clean", seed=5)
    case = manifest.cases[0]
    document = load_document_from_path(tmp_path / case.path)

    result = ax.AnthropicExtractor().extract(document)
    assert result.gross_pay.value is not None
    assert abs(result.gross_pay.value - case.fields.gross_pay) <= 1.0
    assert result.gross_pay.grounded
    assert result.employee_name.value == case.fields.employee_name
