"""Deterministic plaintext paystub renderer.

A fixed, line-based layout so later pipeline stages can ground each extracted
figure in a stable location (document id plus line). The renderer draws the
values it is given: for a tampered document the generator passes a display copy
whose per-period figures are inflated while the year-to-date totals stay true,
which is exactly the inconsistency the engine is meant to catch.
"""

from __future__ import annotations

from .schema import PaystubFields


def render_paystub(displayed: PaystubFields) -> str:
    lines = [
        "PAYSTUB",
        f"Employer: {displayed.employer_name}",
        f"Employee: {displayed.employee_name}",
        f"Pay Frequency: {displayed.pay_frequency}",
        f"Pay Period: {displayed.pay_period_start.isoformat()} to "
        f"{displayed.pay_period_end.isoformat()}",
        f"Pay Date: {displayed.pay_date.isoformat()}",
        "",
        "Earnings",
        f"  Gross Pay (this period): {displayed.gross_pay:.2f}",
        f"  Deductions (this period): {displayed.deductions:.2f}",
        f"  Net Pay (this period): {displayed.net_pay:.2f}",
        "",
        "Year to Date",
        f"  YTD Gross: {displayed.ytd_gross:.2f}",
        f"  YTD Net: {displayed.ytd_net:.2f}",
        f"  Annualized Gross: {displayed.annualized_gross:.2f}",
    ]
    return "\n".join(lines) + "\n"
