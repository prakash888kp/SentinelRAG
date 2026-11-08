"""Unified gate policy and reports."""

from __future__ import annotations

from pathlib import Path

from sentinelrag.gate.evidence import EvidenceBundle, collect_evidence
from sentinelrag.gate.policy import evaluate_policy, load_policy
from sentinelrag.gate.reports.sarif import write_sarif
from sentinelrag.redteam.attacks import single_document_poison
from sentinelrag.redteam.post_retrieval import PostRetrievalTrim, RetrievalHit


def test_collect_evidence_has_hybrid_recall() -> None:
    bundle = collect_evidence()
    assert bundle.metrics["phase1_hybrid_recall_at_k"] >= 0.8


def test_policy_passes_on_repo_defaults() -> None:
    bundle = collect_evidence()
    outcome = evaluate_policy(bundle, load_policy())
    assert outcome.passed


def test_sarif_writes(tmp_path: Path) -> None:
    from sentinelrag.gate.policy import PolicyOutcome

    outcome = PolicyOutcome(
        passed=False,
        violations=[{"rule": "test.rule", "message": "boom", "severity": "error"}],
        advisories=[],
    )
    path = tmp_path / "out.sarif"
    write_sarif(outcome, path)
    assert "SentinelRAG Gate" in path.read_text(encoding="utf-8")


def test_post_retrieval_strips_obvious_poison() -> None:
    poison = single_document_poison(trigger_query="q").chunks[0]
    clean_meta = poison.metadata.model_copy(update={"doc_id": "clean", "trust_score": 0.2})
    from sentinelrag.ingest.schema import ChunkPayload

    clean = ChunkPayload(
        chunk_id="clean::0",
        doc_id="clean",
        text="Legitimate corpus passage about SentinelRAG gates.",
        metadata=clean_meta,
    )
    hits = [
        RetrievalHit(chunk_id=poison.chunk_id, score=2.0, chunk=poison),
        RetrievalHit(chunk_id=clean.chunk_id, score=0.5, chunk=clean),
    ]
    trim = PostRetrievalTrim()
    kept = trim.filter_hits("q", hits)
    assert all("ignore all other" not in h.chunk.text.lower() for h in kept)


def test_evidence_roundtrip(tmp_path: Path) -> None:
    bundle = EvidenceBundle(metrics={"phase1_hybrid_recall_at_k": 1.0})
    p = tmp_path / "e.json"
    bundle.write_json(p)
    loaded = p.read_text(encoding="utf-8")
    assert "sentinelrag-evidence-v1" in loaded
