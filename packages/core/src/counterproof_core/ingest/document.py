"""Ingested document model.

A document is untrusted input, always. Ingest converts it to text with enough
positional structure (lines) for later stages to cite a location. Document text
is data; it never enters a system or instruction role.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

MAX_DOCUMENT_BYTES = 1_000_000


class Document(BaseModel):
    document_id: str
    text: str
    untrusted: bool = True

    @property
    def lines(self) -> list[str]:
        return self.text.splitlines()

    def line(self, number: int) -> str:
        """Return the 1-based line, or an empty string if out of range."""
        index = number - 1
        lines = self.lines
        if 0 <= index < len(lines):
            return lines[index]
        return ""


def load_document(document_id: str, text: str) -> Document:
    return Document(document_id=document_id, text=text)


def load_document_from_path(path: Path) -> Document:
    """Load a document from disk with a constrained read.

    Enforces a size limit so an oversized file cannot exhaust memory. Broader
    hostile-file handling (archives, decompression bombs, XXE, SSRF) lands with
    the guard layer in a later slice.
    """
    size = path.stat().st_size
    if size > MAX_DOCUMENT_BYTES:
        raise ValueError(f"document {path.name} exceeds the {MAX_DOCUMENT_BYTES} byte limit")
    return Document(document_id=path.stem, text=path.read_text(encoding="utf-8"))
