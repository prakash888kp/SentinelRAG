"""Defense hooks for poisoning and metadata attacks."""

from __future__ import annotations

from sentinelrag.ingest.filters import PoisoningFilter
from sentinelrag.ingest.schema import DocumentMetadata


class MetadataTrustFilter(PoisoningFilter):
    """Drop ingest when trust_score is out of schema or suspiciously high."""

    def __init__(self, *, max_trust: float = 1.0) -> None:
        self._max_trust = max_trust

    def accept(self, metadata: DocumentMetadata, text: str) -> bool:
        _ = text
        return metadata.trust_score <= self._max_trust


class LexicalAnomalyFilter(PoisoningFilter):
    """Cheap anomaly signal: block obvious injection phrases."""

    _BLOCKED = ("ignore all other", "compromised", "cryptocurrency miner", "override answers")

    def accept(self, metadata: DocumentMetadata, text: str) -> bool:
        _ = metadata
        lowered = text.lower()
        return not any(phrase in lowered for phrase in self._BLOCKED)
