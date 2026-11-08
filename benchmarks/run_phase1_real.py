#!/usr/bin/env python3
"""Phase 1 retrieval with real sentence-transformers embedder (not for CI)."""

from __future__ import annotations

import json
import os

from sentinelrag.eval.phase1_retrieval import run_benchmark
from sentinelrag.paths import project_root, public_corpus_dir, public_qrels_path
from sentinelrag.settings import settings_without_dotenv


def main() -> int:
    model = os.environ.get("SENTINELRAG_EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
    cfg = settings_without_dotenv(
        embedding_model=model,
        reranker_model="mock-reranker",
        vector_store_backend="memory",
    )
    root = project_root()
    mini = run_benchmark(settings=cfg)
    public = run_benchmark(
        settings=cfg,
        corpus_dir=public_corpus_dir(),
        qrels_path=public_qrels_path(),
    )
    out = {
        "mode": "real_embedder",
        "embedding_model": model,
        "reranker_model": "mock-reranker",
        "mini_corpus": mini,
        "public_corpus": public,
    }
    path = root / "benchmarks" / "phase1_retrieval_real.json"
    path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {path}")
    for label, report in ("mini", mini), ("public", public):
        for row in report["results"]:
            print(
                f"{label} {row['strategy']}: "
                f"recall={row['recall_at_k']:.4f} hit={row.get('hit_rate_at_k', 0):.4f} "
                f"mrr={row['mrr']:.4f}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
