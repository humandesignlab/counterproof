"""Ingest and normalize stage.

Converts each document to text and lightweight structure with positional
metadata so later stages can cite a location. Every document is tagged untrusted
and its content is never placed in a system or instruction role.

v1 supports plaintext documents. Broader format and hostile-file handling lands
with the guard layer in a later slice.
"""

from .document import MAX_DOCUMENT_BYTES, Document, load_document, load_document_from_path

__all__ = [
    "MAX_DOCUMENT_BYTES",
    "Document",
    "load_document",
    "load_document_from_path",
]
