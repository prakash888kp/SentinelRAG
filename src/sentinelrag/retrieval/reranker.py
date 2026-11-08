"""Cross-encoder reranker interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from functools import lru_cache

from sentinelrag.ingest.schema import ChunkPayload


class Reranker(ABC):
    @abstractmethod
    def score(self, query: str, chunks: list[ChunkPayload]) -> list[tuple[str, float]]:
        """Return ``(chunk_id, score)`` sorted by descending relevance."""


class MockReranker(Reranker):
    """Lexical overlap mock for offline CI."""

    def __init__(self, model_name: str = "mock-reranker") -> None:
        self.model_name = model_name

    def score(self, query: str, chunks: list[ChunkPayload]) -> list[tuple[str, float]]:
        q_tokens = set(query.lower().split())
        scored: list[tuple[str, float]] = []
        for chunk in chunks:
            c_tokens = set(chunk.text.lower().split())
            overlap = len(q_tokens & c_tokens)
            scored.append((chunk.chunk_id, float(overlap)))
        return sorted(scored, key=lambda x: -x[1])


@lru_cache(maxsize=4)
def build_reranker(model_name: str) -> Reranker:
    """Build (and cache) a reranker. Real CEs are expensive to load — never rebuild per query."""
    if model_name == "mock-reranker":
        return MockReranker(model_name=model_name)
    try:
        from sentence_transformers import CrossEncoder
    except ImportError as exc:
        msg = f"Reranker {model_name!r} requires uv sync --extra ml"
        raise RuntimeError(msg) from exc

    class _CEReranker(Reranker):
        def __init__(self) -> None:
            self.model_name = model_name
            self._model = CrossEncoder(model_name)

        def score(self, query: str, chunks: list[ChunkPayload]) -> list[tuple[str, float]]:
            if not chunks:
                return []
            pairs = [[query, c.text] for c in chunks]
            raw = self._model.predict(pairs)
            scored = [(chunks[i].chunk_id, float(raw[i])) for i in range(len(chunks))]
            return sorted(scored, key=lambda x: -x[1])

    return _CEReranker()
