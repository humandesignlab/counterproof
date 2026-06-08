"""Guardrail stage.

Assumes the document submitter is an adversary. Defends against hostile text
(prompt injection, never treating document content as instructions) and hostile
files (size, page, and time limits, no external entity resolution, no fetching
of referenced URLs or resources, rejection of archives and decompression bombs),
and validates every model output against its strict schema before use.

Skeleton only in Task 1. No guard logic yet.
"""
