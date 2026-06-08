"""Counterproof synthetic-data package.

Generates synthetic documents (paystubs, bank statements) and a ground-truth
manifest so the eval harness can score exactly. Synthetic data only: this package
never reads, requests, or emits real PII or real financial documents.

Task 1 ships the package skeleton and the manifest output location only. The
generator itself lands in T2.
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
