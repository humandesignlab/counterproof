"""Counterproof verification engine.

The engine is the product: a transparent, reproducible pipeline that re-derives
underwriting figures from untrusted source documents, grounds them in citations,
cross-validates, detects disagreements with a primary system, scores confidence,
and emits an auditable challenge report. It never makes the underwriting decision.

Task 1 ships the package skeleton only. Pipeline stages land in later slices.
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
