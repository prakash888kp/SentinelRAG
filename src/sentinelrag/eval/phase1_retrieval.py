"""Phase 1 retrieval benchmark (library entry for scripts and tests)."""

from __future__ import annotations

import hashlib
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sentinelrag.eval.metrics import hit_rate_at_k, mrr, recall_at_k
from sentinelrag.ingest.pipeline import IndexState, ingest_corpus_dir
from sentinelrag.paths import mini_corpus_dir, mini_qrels_path
from sentinelrag.retrieval.reranker import build_reranker
from sentinelrag.retrieval.strategies import HybridRerankRetriever, NaiveRetriever, StrategyName
from sentinelrag.settings import Settings, settings_without_dotenv


def _default_benchmark_settings() -> Settings:
    """Offline benchmark defaults (mock embedder; ignores ``.env`` file only)."""
    return settings_without_dotenv(
        embedding_model="mock-embedder",
        reranker_model="mock-reranker",
        vector_store_backend="memory",
    )


def corpus_content_hash(corpus_dir: Path) -> str:
    digests: list[str] = []
    for path in sorted(corpus_dir.glob("*.md")):
        digests.append(hashlib.sha256(path.read_bytes()).hexdigest())
    joined = "|".join(digests)
    return hashlib.sha256(joined.encode()).hexdigest()[:16]


def load_qrels(path: Path) -> tuple[int, list[dict[str, Any]]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    seed = int(payload.get("seed", 42))
    queries = list(payload.get("queries", []))
    return seed, queries


def run_benchmark(
    *,
    settings: Settings | None = None,
    strategies: tuple[StrategyName, ...] = ("naive", "hybrid"),
    corpus_dir: Path | None = None,
    qrels_path: Path | None = None,
) -> dict[str, Any]:
    cfg = settings if settings is not None else _default_benchmark_settings()
    corpus_dir = corpus_dir if corpus_dir is not None else mini_corpus_dir()
    qrels_path = qrels_path if qrels_path is not None else mini_qrels_path()
    seed, qrels = load_qrels(qrels_path)

    state = IndexState()
    ingest_corpus_dir(corpus_dir, state, settings=cfg)
    assert state.store is not None and state.embedder is not None

    embedder = state.embedder
    k = cfg.retrieval_top_k
    rows: list[dict[str, Any]] = []

    for strategy in strategies:
        retriever: NaiveRetriever | HybridRerankRetriever
        if strategy == "naive":
            retriever = NaiveRetriever(state.store, embedder)
        else:
            retriever = HybridRerankRetriever(
                state.store,
                state.bm25,
                embedder,
                build_reranker(cfg.reranker_model),
                alpha=cfg.hybrid_alpha,
                chunks_by_id=state.chunks,
            )
        recalls: list[float] = []
        hits_rate: list[float] = []
        mrrs: list[float] = []
        latencies: list[float] = []
        for item in qrels:
            query = str(item["query"])
            relevant = set(item["relevant_chunk_ids"])

            t0 = time.perf_counter()
            retrieved_ids = [h.chunk_id for h in retriever.retrieve(query, top_k=k)]
            latencies.append((time.perf_counter() - t0) * 1000.0)
            recalls.append(recall_at_k(retrieved_ids, relevant, k=k))
            hits_rate.append(hit_rate_at_k(retrieved_ids, relevant, k=k))
            mrrs.append(mrr(retrieved_ids, relevant))
        rows.append(
            {
                "strategy": strategy,
                "recall_at_k": sum(recalls) / len(recalls) if recalls else 0.0,
                "hit_rate_at_k": sum(hits_rate) / len(hits_rate) if hits_rate else 0.0,
                "mrr": sum(mrrs) / len(mrrs) if mrrs else 0.0,
                "latency_ms_mean": sum(latencies) / len(latencies) if latencies else 0.0,
            }
        )

    return {
        "generated_at": datetime.now(tz=UTC).isoformat(),
        "embedding_model": cfg.embedding_model,
        "reranker_model": cfg.reranker_model,
        "corpus_hash": corpus_content_hash(corpus_dir),
        "seed": seed,
        "retrieval_top_k": k,
        "hybrid_alpha": cfg.hybrid_alpha,
        "results": rows,
    }
