"""Extractor interface.

Both the deterministic (reproducible, CI-scored) extractor and the Anthropic
tool-use extractor satisfy this protocol, so downstream stages depend on the
contract, not the implementation.
"""

from __future__ import annotations

from typing import Protocol

from ..ingest.document import Document
from .schema import PaystubExtraction


class Extractor(Protocol):
    def extract(self, document: Document) -> PaystubExtraction: ...
