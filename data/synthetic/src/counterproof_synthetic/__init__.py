"""Counterproof synthetic-data package.

Generates synthetic documents (paystubs, bank statements) and a ground-truth
manifest so the eval harness can score exactly. Synthetic data only: this package
never reads, requests, or emits real PII or real financial documents.

It generates paystubs (clean and tampered variants) plus a ground-truth manifest
the eval harness can score against.
"""

__version__ = "0.1.0"

from .generator import MANIFEST_FILENAME, generate_set
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

__all__ = [
    "__version__",
    "MANIFEST_FILENAME",
    "generate_set",
    "render_paystub",
    "PERIODS_PER_YEAR",
    "Classification",
    "DocumentRecord",
    "IssueRecord",
    "Manifest",
    "PayFrequency",
    "PaystubFields",
    "RecommendedAction",
    "SetVariant",
    "Variant",
]
