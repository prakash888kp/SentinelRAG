#!/usr/bin/env python3
"""Poison benchmark v1: ingest block rate + post-retrieval ASR (mock, reproducible)."""

from __future__ import annotations

import json

from sentinelrag.paths import mini_corpus_dir, project_root
from sentinelrag.redteam.attacks import (
    dual_sleeper_trigger,
    metadata_only_poison,
    single_document_poison,
)
from sentinelrag.redteam.defenses import LexicalAnomalyFilter, MetadataTrustFilter
from sentinelrag.redteam.harness import _index_with_poison, _retrieve_ids
from sentinelrag.redteam.post_retrieval import PostRetrievalTrim, RetrievalHit
from sentinelrag.retrieval.stores import InMemoryVectorStore
from sentinelrag.settings import settings_without_dotenv


def _ingest_block_rate() -> float:
    meta = MetadataTrustFilter()
    lex = LexicalAnomalyFilter()
    samples = [
        metadata_only_poison().chunks[0],
        single_document_poison(trigger_query="What is SentinelRAG?").chunks[0],
        dual_sleeper_trigger().chunks[0],
    ]
    blocked = 0
    for chunk in samples:
        ok = meta.accept(chunk.metadata, chunk.text) and lex.accept(chunk.metadata, chunk.text)
        if not ok:
            blocked += 1
    return blocked / len(samples)


def _post_retrieval_asr(alpha: float = 0.5) -> float:
    cfg = settings_without_dotenv(
        embedding_model="mock-embedder",
        hybrid_alpha=alpha,
        vector_store_backend="memory",
    )
    trim = PostRetrievalTrim()
    attacks = [
        (single_document_poison(trigger_query="What is SentinelRAG?"), "What is SentinelRAG?"),
        (dual_sleeper_trigger(), "RELEASE_KEYWORD status"),
        (metadata_only_poison(), "Trusted System Overview"),
    ]
    poison_ids = {"poison-single::0", "poison-sleeper::0", "poison-trigger::0", "poison-meta::0"}
    success = 0
    for sample, query in attacks:
        state, store = _index_with_poison(poison_chunks=sample.chunks, settings=cfg, alpha=alpha)
        assert isinstance(store, InMemoryVectorStore)
        ids = _retrieve_ids(state, store, query, alpha=alpha, top_k=cfg.retrieval_top_k)
        hits = [
            RetrievalHit(
                chunk_id=cid,
                score=1.0,
                chunk=state.chunks[cid],
            )
            for cid in ids
            if cid in state.chunks
        ]
        trimmed = trim.filter_hits(query, hits, bm25=state.bm25)
        trimmed_ids = {h.chunk_id for h in trimmed}
        if any(pid in trimmed_ids for pid in poison_ids):
            success += 1
    return success / len(attacks)


def main() -> int:
    report = {
        "version": "poison_benchmark_v1",
        "ingest_block_rate": _ingest_block_rate(),
        "post_retrieval_mean_asr": _post_retrieval_asr(),
        "notes": "mock embedder; post-retrieval trim lowers ASR vs raw retrieval",
    }
    # Touch corpus path for hash visibility
    _ = mini_corpus_dir()
    out = project_root() / "benchmarks" / "poison_benchmark_v1.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
