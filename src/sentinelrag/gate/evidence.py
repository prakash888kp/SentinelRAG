"""Versioned evidence artifacts for CI and audit trails."""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from sentinelrag.paths import project_root
from sentinelrag.settings import Settings, settings_without_dotenv

SCHEMA_ID = "sentinelrag-evidence-v1"

BindingMode = Literal["fixture", "app"]


@dataclass(slots=True)
class ChunkerConfig:
    """Chunker knobs exercised when evidence was collected."""

    strategy: str
    chunk_size: int
    chunk_overlap: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class EvidenceBundle:
    """Machine-readable gate input/output."""

    schema: str = SCHEMA_ID
    generated_at: str = field(default_factory=lambda: datetime.now(tz=UTC).isoformat())
    project: str = "SentinelRAG"
    commit: str | None = None
    app_revision: str | None = None
    chunker_config: dict[str, Any] | None = None
    binding_mode: BindingMode = "fixture"
    metrics: dict[str, Any] = field(default_factory=dict)
    security_probes: dict[str, Any] = field(default_factory=dict)
    violations: list[dict[str, str]] = field(default_factory=list)
    passed: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def write_json(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")


def chunker_config_from_settings(settings: Settings) -> ChunkerConfig:
    return ChunkerConfig(
        strategy=settings.chunk_strategy,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )


def resolve_app_revision(*, root: Path | None = None) -> str | None:
    """Prefer explicit env, then GitHub Actions SHA, then local git HEAD."""
    for key in ("SENTINELRAG_APP_REVISION", "GITHUB_SHA"):
        value = os.environ.get(key, "").strip()
        if value:
            return value
    root = root or project_root()
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    sha = proc.stdout.strip()
    return sha or None


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
                "hit_rate_at_k": float(row.get("hit_rate_at_k", row["recall_at_k"])),
                "latency_ms_mean": float(row.get("latency_ms_mean", 0.0)),
            }
    return {"recall_at_k": 0.0, "mrr": 0.0, "hit_rate_at_k": 0.0, "latency_ms_mean": 0.0}


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

    settings = settings_without_dotenv(
        embedding_model="mock-embedder",
        reranker_model="mock-reranker",
        vector_store_backend="memory",
    )
    # Prefer chunker stamp from the last Phase 1 refresh when present.
    phase1_chunker = phase1.get("chunker_config")
    chunker = (
        dict(phase1_chunker)
        if isinstance(phase1_chunker, dict)
        else chunker_config_from_settings(settings).to_dict()
    )
    revision = resolve_app_revision(root=root)
    bundle = EvidenceBundle(
        commit=revision,
        app_revision=revision,
        chunker_config=chunker,
        binding_mode="fixture",
        metrics={
            "phase1_hybrid_recall_at_k": hybrid["recall_at_k"],
            "phase1_hybrid_mrr": hybrid["mrr"],
            "phase1_hybrid_hit_rate_at_k": hybrid["hit_rate_at_k"],
            "phase1_hybrid_latency_ms_mean": hybrid["latency_ms_mean"],
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
            "hygiene": _load_json(bench / "hygiene_report.json"),
            "provenance": _load_json(bench / "corpus_manifest.json"),
        },
    )
    return bundle
