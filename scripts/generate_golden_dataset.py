#!/usr/bin/env python3
"""Generate golden RAG eval set from mini corpus (fixed seed)."""

from __future__ import annotations

import json
import random
from pathlib import Path

from sentinelrag.paths import project_root

SEED = 42


def main() -> int:
    rng = random.Random(SEED)
    _ = rng  # reserved for future synthetic expansion

    items = [
        {
            "id": "sh-01",
            "type": "single_hop",
            "query": "What is SentinelRAG?",
            "relevant_chunk_ids": ["01-overview::0"],
            "expected_answer_contains": ["SentinelRAG", "eval"],
        },
        {
            "id": "sh-02",
            "type": "single_hop",
            "query": "Name three chunking strategies in Phase 1.",
            "relevant_chunk_ids": ["02-ingest::0"],
            "expected_answer_contains": ["fixed", "semantic", "contextual"],
        },
        {
            "id": "sh-03",
            "type": "single_hop",
            "query": "What does hybrid retrieval fuse?",
            "relevant_chunk_ids": ["03-retrieval::0"],
            "expected_answer_contains": ["BM25", "dense"],
        },
        {
            "id": "mh-01",
            "type": "multi_hop",
            "query": (
                "How do ingestion chunking choices and retrieval metrics connect "
                "in Phase 1 benchmarks?"
            ),
            "relevant_chunk_ids": ["02-ingest::0", "04-eval::0"],
            "expected_answer_contains": ["chunk", "recall", "MRR"],
        },
        {
            "id": "mh-02",
            "type": "multi_hop",
            "query": "How do security defenses relate to eval CI gates?",
            "relevant_chunk_ids": ["04-eval::0", "05-security::0"],
            "expected_answer_contains": ["poison", "CI"],
        },
    ]

    payload = {
        "seed": SEED,
        "corpus_version": "mini_corpus_v1",
        "generated_by": "scripts/generate_golden_dataset.py",
        "items": items,
    }
    out = project_root() / "data" / "golden_dataset.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out} ({len(items)} items)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
