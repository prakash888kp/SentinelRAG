"""Phase 1 benchmark runner smoke test."""

from __future__ import annotations

from sentinelrag.eval.phase1_retrieval import run_benchmark
from sentinelrag.settings import Settings


def test_run_benchmark_offline() -> None:
    report = run_benchmark(settings=Settings(_env_file=None))
    assert report["embedding_model"] == "mock-embedder"
    assert report["seed"] == 42
    assert len(report["results"]) == 2
    for row in report["results"]:
        assert 0.0 <= row["recall_at_k"] <= 1.0
        assert 0.0 <= row["mrr"] <= 1.0
