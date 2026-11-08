"""Copy to your repo as adapter.py for sentinelrag-gate."""

from __future__ import annotations

from typing import Any


def collect_metrics() -> dict[str, Any]:
    """Wire your RAG pipeline metrics here."""
    return {
        "metrics": {
            "phase1_hybrid_recall_at_k": 0.95,
            "phase2_mean_faithfulness": 0.80,
            "phase2_mean_relevance": 0.90,
        },
        "security_probes": {
            "ingest_defense_blocked_fraction": 1.0,
            "poison_benchmark_v1": {
                "ingest_block_rate": 1.0,
                "post_retrieval_mean_asr": 0.0,
            },
        },
    }
