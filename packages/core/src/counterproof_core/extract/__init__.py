"""Independent extraction stage.

Re-derives a focused set of underwriting-relevant fields via tool use and a
strict typed schema, each value carrying per-field confidence and source spans.
This re-derives a small figure set; it is not a primary OCR or extraction engine.

v1 re-derives the paystub field set. Two implementations satisfy the Extractor
protocol: a deterministic, reproducible parser (scored in CI) and an Anthropic
tool-use extractor (the product path, exercised by a gated integration test).
"""

from .base import Extractor
from .deterministic import (
    MODEL_VERSION as DETERMINISTIC_MODEL_VERSION,
)
from .deterministic import (
    PROMPT_VERSION as DETERMINISTIC_PROMPT_VERSION,
)
from .deterministic import (
    DeterministicExtractor,
)
from .schema import (
    GROUNDED_CONFIDENCE,
    UNGROUNDED_CONFIDENCE,
    ExtractedField,
    PaystubExtraction,
)

__all__ = [
    "Extractor",
    "DeterministicExtractor",
    "DETERMINISTIC_MODEL_VERSION",
    "DETERMINISTIC_PROMPT_VERSION",
    "ExtractedField",
    "PaystubExtraction",
    "GROUNDED_CONFIDENCE",
    "UNGROUNDED_CONFIDENCE",
]
