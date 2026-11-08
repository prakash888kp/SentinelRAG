"""Versioned evidence artifacts for CI and audit trails."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sentinelrag.paths import project_root

SCHEMA_ID = "sentinelrag-evidence-v1"


@dataclass(slots=True)
class EvidenceBundle:
    """Machine-readable gate input/output."""

    schema: str = SCHEMA_ID
    generated_at: str = field(default_factory=lambda: datetime.now(tz=UTC).isoformat())
    project: str = "SentinelRAG"
    commit: str | None = None
    metrics: dict[str, Any] = field(default_factory=dict)
    security_probes: dict[str, Any] = field(default_factory=dict)
    violations: list[dict[str, str]] = field(default_factory=list)
    passed: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def write_json(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def _hybrid_row(phase1: dict[str, Any]) -> dict[str, float]:
    for row in phase1.get("results", []):
        if row.get("strategy") == "hybrid":
            return {
                "recall_at_k": float(row["recall_at_k"]),
                "mrr": float(row["mrr"]),
            }
    return {"recall_at_k": 0.0, "mrr": 0.0}


def collect_evidence(*, root: Path | None = None) -> EvidenceBundle:
    """Aggregate committed benchmark JSON into one evidence bundle (offline)."""
    root = root or project_root()
    bench = root / "benchmarks"
    phase1 = _load_json(bench / "phase1_retrieval.json")
    phase2 = _load_json(bench / "phase2_eval.json")
    public = _load_json(bench / "public_retrieval.json")
    redteam = _load_json(bench / "asr_vs_alpha.json")
    poison = _load_json(bench / "poison_benchmark_v1.json")

    hybrid = _hybrid_row(phase1)
    public_hybrid = _hybrid_row(public)

    alpha_ref = 0.5
    defense_frac = 0.0
    mean_asr = 0.0
    for row in redteam.get("sweep", []):
        if row.get("alpha") == alpha_ref:
            defense_frac = float(row.get("defense_probe_blocked_fraction", 0.0))
            mean_asr = float(row.get("mean_retrieval_asr", 0.0))
            break

    bundle = EvidenceBundle(
        metrics={
            "phase1_hybrid_recall_at_k": hybrid["recall_at_k"],
            "phase1_hybrid_mrr": hybrid["mrr"],
            "phase2_mean_faithfulness": float(phase2.get("mean_faithfulness", 0.0)),
            "phase2_mean_relevance": float(phase2.get("mean_relevance", 0.0)),
            "phase2_mean_recall_at_k": float(phase2.get("mean_recall_at_k", 0.0)),
            "public_hybrid_recall_at_k": public_hybrid["recall_at_k"],
            "public_naive_recall_at_k": next(
                (
                    float(r["recall_at_k"])
                    for r in public.get("results", [])
                    if r.get("strategy") == "naive"
                ),
                0.0,
            ),
            "redteam_mean_retrieval_asr_alpha_0_5": mean_asr,
        },
        security_probes={
            "ingest_defense_blocked_fraction": defense_frac,
            "poison_benchmark_v1": poison,
        },
    )
    return bundle
