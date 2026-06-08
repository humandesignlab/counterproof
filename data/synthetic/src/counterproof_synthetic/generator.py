"""Seedable synthetic paystub generator.

Produces internally consistent paystubs and a ground-truth manifest. Synthetic
data only: names and employers come from small builtin pools, never real PII.

Variants:
  - clean: the document matches the true, reconciled values.
  - tampered (altered_income): the displayed per-period gross (and net) are
    inflated while the year-to-date totals stay true, so the per-period figure no
    longer reconciles with YTD. The manifest records the true values and labels
    the planted defect.
"""

from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

from . import __version__
from .paystub import render_paystub
from .schema import (
    PERIODS_PER_YEAR,
    Classification,
    DocumentRecord,
    IssueRecord,
    Manifest,
    PayFrequency,
    PaystubFields,
    RecommendedAction,
    SetVariant,
    Variant,
)

MANIFEST_FILENAME = "manifest.json"

_FIRST_NAMES: list[str] = [
    "Avery",
    "Jordan",
    "Riley",
    "Morgan",
    "Casey",
    "Quinn",
    "Reese",
    "Sawyer",
    "Devin",
    "Harper",
]
_LAST_NAMES: list[str] = [
    "Sample",
    "Synthetic",
    "Testerly",
    "Fixture",
    "Mockton",
    "Placeholder",
    "Exampleton",
    "Dummett",
]
_EMPLOYERS: list[str] = [
    "Northwind Synthetic Co",
    "Acme Fixtures LLC",
    "Globex Test Industries",
    "Initech Sample Corp",
    "Umbrella Mock Group",
    "Hooli Demo Inc",
]
_FREQUENCIES: list[PayFrequency] = ["weekly", "biweekly", "semimonthly", "monthly"]

_PERIOD_DAYS: dict[PayFrequency, int] = {
    "weekly": 7,
    "biweekly": 14,
    "semimonthly": 15,
    "monthly": 30,
}

_BASE_DATE = date(2025, 1, 1)


def _round2(value: float) -> float:
    return round(value, 2)


def _pick_detectable_shown_gross(rng: random.Random, true_gross: float, ytd_gross: float) -> float:
    """Inflate per-period gross so YTD/per-period is clearly not an integer.

    Keeps the planted altered_income defect honestly detectable by the engine's
    YTD-vs-per-period check, rather than relying on a coincidental ratio.
    """
    for _ in range(64):
        factor = round(rng.uniform(1.25, 1.6), 2)
        shown = _round2(true_gross * factor)
        if shown <= true_gross:
            continue
        ratio = ytd_gross / shown
        if abs(ratio - round(ratio)) > 0.1:
            return shown
    return _round2(true_gross * 1.37)


def _build_true_fields(rng: random.Random) -> PaystubFields:
    employee = f"{rng.choice(_FIRST_NAMES)} {rng.choice(_LAST_NAMES)}"
    employer = rng.choice(_EMPLOYERS)
    frequency = rng.choice(_FREQUENCIES)
    periods_per_year = PERIODS_PER_YEAR[frequency]

    gross = _round2(rng.uniform(1500.0, 6000.0))
    deductions = _round2(gross * rng.uniform(0.18, 0.32))
    net = _round2(gross - deductions)
    annualized = _round2(gross * periods_per_year)

    periods_elapsed = rng.randint(1, periods_per_year)
    ytd_gross = _round2(gross * periods_elapsed)
    ytd_net = _round2(net * periods_elapsed)

    length = _PERIOD_DAYS[frequency]
    start = _BASE_DATE + timedelta(days=length * (periods_elapsed - 1))
    end = start + timedelta(days=length - 1)
    pay_date = end + timedelta(days=5)

    return PaystubFields(
        employee_name=employee,
        employer_name=employer,
        pay_frequency=frequency,
        pay_period_start=start,
        pay_period_end=end,
        pay_date=pay_date,
        gross_pay=gross,
        deductions=deductions,
        net_pay=net,
        ytd_gross=ytd_gross,
        ytd_net=ytd_net,
        annualized_gross=annualized,
    )


def _is_tampered(variant: SetVariant, index: int) -> bool:
    if variant == "clean":
        return False
    if variant == "tampered":
        return True
    return index % 2 == 1


def _build_record(
    rng: random.Random, document_id: str, tampered: bool
) -> tuple[DocumentRecord, str]:
    true_fields = _build_true_fields(rng)

    issue: IssueRecord | None
    variant_label: Variant
    classification: Classification
    action: RecommendedAction

    if tampered:
        shown_gross = _pick_detectable_shown_gross(
            rng, true_fields.gross_pay, true_fields.ytd_gross
        )
        shown_net = _round2(shown_gross - true_fields.deductions)
        shown_annual = _round2(shown_gross * PERIODS_PER_YEAR[true_fields.pay_frequency])
        displayed = true_fields.model_copy(
            update={
                "gross_pay": shown_gross,
                "net_pay": shown_net,
                "annualized_gross": shown_annual,
            }
        )
        issue = IssueRecord(
            type="altered_income",
            field="gross_pay",
            shown_value=shown_gross,
            true_value=true_fields.gross_pay,
            note=(
                "Displayed gross pay inflated; per-period gross no longer "
                "reconciles with year-to-date totals."
            ),
        )
        variant_label = "tampered"
        classification = "material_discrepancy"
        action = "review"
    else:
        displayed = true_fields
        issue = None
        variant_label = "clean"
        classification = "match"
        action = "pass"

    record = DocumentRecord(
        document_id=document_id,
        path=f"{document_id}.txt",
        variant=variant_label,
        fields=true_fields,
        injected_issue=issue,
        expected_classification=classification,
        expected_recommended_action=action,
    )
    return record, render_paystub(displayed)


def generate_set(
    out_dir: Path,
    count: int = 10,
    variant: SetVariant = "mixed",
    seed: int = 0,
) -> Manifest:
    """Generate a paystub set plus its manifest into out_dir and return the manifest."""
    if count < 1:
        raise ValueError("count must be at least 1")

    rng = random.Random(seed)
    out_dir.mkdir(parents=True, exist_ok=True)

    cases: list[DocumentRecord] = []
    for index in range(count):
        document_id = f"paystub-{index + 1:04d}"
        record, text = _build_record(rng, document_id, _is_tampered(variant, index))
        (out_dir / record.path).write_text(text, encoding="utf-8")
        cases.append(record)

    manifest = Manifest(generator_version=__version__, seed=seed, cases=cases)
    (out_dir / MANIFEST_FILENAME).write_text(
        manifest.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    return manifest
