#!/usr/bin/env python3
"""Phase 3 trajectory benchmark on golden multi-hop queries."""

from __future__ import annotations

import json

from sentinelrag.eval.phase2_rag import golden_dataset_path
from sentinelrag.eval.trajectory import trajectory_recall, trajectory_usefulness
from sentinelrag.ingest.pipeline import IndexState, ingest_corpus_dir
from sentinelrag.paths import mini_corpus_dir, project_root
from sentinelrag.retrieval.agentic import AgenticMultiHopRetriever
from sentinelrag.retrieval.reranker import build_reranker
from sentinelrag.retrieval.strategies import HybridRerankRetriever
from sentinelrag.settings import settings_without_dotenv


def main() -> int:
    cfg = settings_without_dotenv(embedding_model="mock-embedder", vector_store_backend="memory")
    golden = json.loads(golden_dataset_path().read_text(encoding="utf-8"))
    state = IndexState()
    ingest_corpus_dir(mini_corpus_dir(), state, settings=cfg)
    assert state.store is not None and state.embedder is not None
    hybrid = HybridRerankRetriever(
        state.store,
        state.bm25,
        state.embedder,
        build_reranker("mock-reranker"),
        alpha=cfg.hybrid_alpha,
        chunks_by_id=state.chunks,
    )
    agent = AgenticMultiHopRetriever(hybrid, max_hops=cfg.agent_max_hops)
    rows = []
    for item in golden["items"]:
        if item["type"] != "multi_hop":
            continue
        result = agent.retrieve(item["query"], top_k=cfg.eval_recall_k)
        rel = set(item["relevant_chunk_ids"])
        rows.append(
            {
                "id": item["id"],
                "trajectory_usefulness": trajectory_usefulness(result.hops),
                "trajectory_recall": trajectory_recall(result.hops, rel),
                "n_hops": len(result.hops),
            }
        )
    report = {
        "mean_trajectory_usefulness": sum(r["trajectory_usefulness"] for r in rows) / len(rows),
        "mean_trajectory_recall": sum(r["trajectory_recall"] for r in rows) / len(rows),
        "items": rows,
    }
    out = project_root() / "benchmarks" / "phase3_trajectory.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
