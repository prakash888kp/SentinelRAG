"""Ingest-time anomaly / poisoning filters (Phase 5 implements real checks)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from sentinelrag.ingest.schema import DocumentMetadata


class PoisoningFilter(ABC):
    @abstractmethod
    def accept(self, metadata: DocumentMetadata, text: str) -> bool:
        """Return False to drop a document during ingest."""


class NoOpPoisoningFilter(PoisoningFilter):
    """Default pass-through filter for Phase 1."""

    def accept(self, metadata: DocumentMetadata, text: str) -> bool:
        _ = metadata, text
        return True
