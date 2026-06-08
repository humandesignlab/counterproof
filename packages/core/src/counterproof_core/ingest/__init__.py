"""Ingest and normalize stage.

Converts each document to text and lightweight structure with positional
metadata so later stages can cite a location. Every document is tagged untrusted
and its content is never placed in a system or instruction role.

Skeleton only in Task 1. No parsing logic yet.
"""
