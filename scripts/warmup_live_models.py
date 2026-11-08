#!/usr/bin/env python3
"""Download/load live embedder + cross-encoder once so the 60s demo stays warm."""

from __future__ import annotations

import time

from sentinelrag.live_models import LIVE_EMBEDDING_MODEL, LIVE_RERANKER_MODEL
from sentinelrag.retrieval.embeddings import build_embedder
from sentinelrag.retrieval.reranker import build_reranker


def main() -> int:
    t0 = time.perf_counter()
    print(f"Loading embedder {LIVE_EMBEDDING_MODEL} …")
    emb = build_embedder(LIVE_EMBEDDING_MODEL, dim=384, seed=42)
    _ = emb.embed("warmup query")
    print(f"Loading reranker {LIVE_RERANKER_MODEL} …")
    rr = build_reranker(LIVE_RERANKER_MODEL)
    from sentinelrag.ingest.schema import ChunkPayload, DocumentMetadata

    meta = DocumentMetadata(doc_id="w", title="w", source="warmup")
    chunk = ChunkPayload(chunk_id="w::0", doc_id="w", text="warmup chunk", metadata=meta)
    _ = rr.score("warmup", [chunk])
    print(f"Warm in {time.perf_counter() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
