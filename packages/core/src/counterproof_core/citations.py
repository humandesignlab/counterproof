"""Shared citation type.

Every extracted figure must point back to where it came from. A value without a
citation is ungrounded and, by rule, low confidence. The report stage reuses this
type so a finding's evidence is the same object the extractor produced.
"""

from __future__ import annotations

from pydantic import BaseModel


class Citation(BaseModel):
    document_id: str
    location: str
    snippet: str
