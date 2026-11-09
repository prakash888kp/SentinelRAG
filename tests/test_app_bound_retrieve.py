"""App-bound Retrieve: harmful chunk-size must fail on remapped cases."""

from __future__ import annotations

import json
from pathlib import Path

from sentinelrag.eval.app_bound_retrieve import (
    remap_relevant_chunk_ids,
    run_app_bound_chunk_regression,
    text_overlap_ratio,
)
from sentinelrag.gate.cli import build_parser
from sentinelrag.gate.evidence import collect_evidence


def test_text_overlap_ratio_identity() -> None:
    assert text_overlap_ratio("hybrid retrieval BM25", "hybrid retrieval BM25") == 1.0


def test_remap_relevant_chunk_ids_finds_overlap() -> None:
    gold = ["SentinelRAG defends RAG pipelines with Retrieve Ground Defend gates."]
    candidates = {
        "a::0": "Unrelated preface text about weather.",
        "a::1": "SentinelRAG defends RAG pipelines with Retrieve Ground Defend gates. Extra.",
    }
    remapped = remap_relevant_chunk_ids(gold_texts=gold, candidate_chunks=candidates)
    assert remapped == {"a::1"}


def test_harmful_chunk_size_fails_retrieve() -> None:
    result = run_app_bound_chunk_regression(
        baseline_chunk_size=500,
        harmful_chunk_size=64,
        harmful_overlap=0,
        min_drop=0.15,
    )
    assert result.passed, result.message
    assert result.harmful_recall < result.baseline_recall
    assert result.baseline_chunker["chunk_size"] == 500
    assert result.harmful_chunker["chunk_size"] == 64
    evidence = result.to_evidence()
    assert evidence.binding_mode == "app"
    assert evidence.chunker_config is not None
    assert "app_bound_baseline_hybrid_recall_at_k" in evidence.metrics


def test_collect_evidence_stamps_chunker_and_revision() -> None:
    bundle = collect_evidence()
    assert bundle.binding_mode == "fixture"
    assert bundle.chunker_config is not None
    assert "chunk_size" in bundle.chunker_config
    assert "strategy" in bundle.chunker_config


def test_cli_app_bound_check(tmp_path: Path) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "app-bound-check",
            "--harmful-chunk-size",
            "64",
            "--out",
            str(tmp_path / "out"),
        ]
    )
    code = args.func(args)
    assert code == 0
    payload = json.loads((tmp_path / "out" / "evidence.json").read_text(encoding="utf-8"))
    assert payload["binding_mode"] == "app"
    assert payload["chunker_config"]["chunk_size"] in (64, 500)
