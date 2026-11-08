"""Post-retrieval trimming before generation (original heuristics)."""

from __future__ import annotations

from dataclasses import dataclass

from sentinelrag.ingest.schema import ChunkPayload
from sentinelrag.retrieval.bm25_index import BM25Index


@dataclass(frozen=True, slots=True)
class RetrievalHit:
    chunk_id: str
    score: float
    chunk: ChunkPayload


class PostRetrievalTrim:
    """Drop outlier poison candidates using lexical + score consensus."""

    _TRIGGERS = (
        "ignore all other",
        "compromised",
        "override answers",
        "cryptocurrency miner",
    )

    def __init__(self, *, z_threshold: float = 2.5) -> None:
        self._z = z_threshold

    def filter_hits(
        self,
        query: str,
        hits: list[RetrievalHit],
        *,
        bm25: BM25Index | None = None,
    ) -> list[RetrievalHit]:
        if not hits:
            return hits
        scores = [h.score for h in hits]
        mean = sum(scores) / len(scores)
        var = sum((s - mean) ** 2 for s in scores) / max(len(scores), 1)
        std = var**0.5 or 1e-9
        kept: list[RetrievalHit] = []
        sparse: dict[str, float] = {}
        if bm25 is not None:
            sparse = dict(bm25.search(query, top_k=len(hits) * 2))
        for hit in hits:
            text = hit.chunk.text.lower()
            if any(t in text for t in self._TRIGGERS):
                continue
            z = abs(hit.score - mean) / std
            if z > self._z and hit.chunk.metadata.trust_score > 0.9:
                continue
            if sparse.get(hit.chunk_id, 0.0) < 0.01 and hit.score > mean + 2 * std:
                continue
            kept.append(hit)
        return kept or hits[:1]
