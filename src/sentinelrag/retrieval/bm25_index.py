"""In-memory BM25 over chunk texts."""

from __future__ import annotations

from rank_bm25 import BM25Okapi

from sentinelrag.ingest.schema import ChunkPayload


class BM25Index:
    def __init__(self) -> None:
        self._chunk_ids: list[str] = []
        self._texts: list[str] = []
        self._bm25: BM25Okapi | None = None

    def clear(self) -> None:
        self._chunk_ids = []
        self._texts = []
        self._bm25 = None

    def add_chunks(self, chunks: list[ChunkPayload]) -> None:
        for chunk in chunks:
            self._chunk_ids.append(chunk.chunk_id)
            self._texts.append(chunk.text)
        tokenized = [_tokenize(t) for t in self._texts]
        self._bm25 = BM25Okapi(tokenized)

    def search(self, query: str, *, top_k: int = 10) -> dict[str, float]:
        if self._bm25 is None or not self._chunk_ids:
            return {}
        scores = self._bm25.get_scores(_tokenize(query))
        ranked = sorted(zip(self._chunk_ids, scores, strict=True), key=lambda x: -x[1])
        return dict(ranked[:top_k])


def _tokenize(text: str) -> list[str]:
    return [t for t in text.lower().split() if t]
