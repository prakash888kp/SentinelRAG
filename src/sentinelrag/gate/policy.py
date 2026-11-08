"""Policy-as-code evaluation over evidence bundles."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from sentinelrag.gate.evidence import EvidenceBundle
from sentinelrag.paths import project_root


@dataclass(frozen=True, slots=True)
class PolicyOutcome:
    passed: bool
    violations: list[dict[str, str]]
    advisories: list[dict[str, str]]


def load_policy(path: Path | None = None) -> dict[str, Any]:
    p = path or (project_root() / "config" / "gate_policy.yaml")
    data: dict[str, Any] = yaml.safe_load(p.read_text(encoding="utf-8"))
    return data


def _viol(
    rule: str, message: str, *, severity: str = "error"
) -> dict[str, str]:
    return {"rule": rule, "message": message, "severity": severity}


def evaluate_policy(
    evidence: EvidenceBundle,
    policy: dict[str, Any],
    *,
    baseline: EvidenceBundle | None = None,
) -> PolicyOutcome:
    violations: list[dict[str, str]] = []
    advisories: list[dict[str, str]] = []
    absolute = policy.get("absolute", {})
    m = evidence.metrics
    s = evidence.security_probes

    p1 = absolute.get("phase1_retrieval", {})
    hybrid_floor = p1.get("hybrid", {})
    if m.get("phase1_hybrid_recall_at_k", 0) < hybrid_floor.get("recall_at_k_min", 0):
        violations.append(
            _viol("phase1.hybrid.recall", f"hybrid recall {m['phase1_hybrid_recall_at_k']}")
        )

    p2 = absolute.get("phase2_rag", {})
    for key, floor_key in (
        ("phase2_mean_faithfulness", "mean_faithfulness_min"),
        ("phase2_mean_relevance", "mean_relevance_min"),
        ("phase2_mean_recall_at_k", "mean_recall_at_k_min"),
    ):
        if m.get(key, 0) < p2.get(floor_key, 0):
            violations.append(_viol(f"phase2.{key}", f"{key} below {p2.get(floor_key)}"))

    p5 = absolute.get("phase5_redteam", {})
    blocked = float(s.get("ingest_defense_blocked_fraction", 0))
    if blocked < p5.get("defense_probe_blocked_fraction_min", 1.0):
        violations.append(_viol("redteam.ingest_defense", f"blocked fraction {blocked}"))

    poison_cfg = absolute.get("poison_benchmark_v1", {})
    poison = s.get("poison_benchmark_v1") or {}
    if poison and poison_cfg:
        post_asr = float(poison.get("post_retrieval_mean_asr", 1.0))
        if post_asr > poison_cfg.get("post_retrieval_asr_max", 1.0):
            violations.append(_viol("poison.post_retrieval_asr", f"ASR {post_asr}"))
        ingest_rate = float(poison.get("ingest_block_rate", 0.0))
        if ingest_rate < poison_cfg.get("ingest_block_rate_min", 1.0):
            violations.append(_viol("poison.ingest_block", f"ingest block rate {ingest_rate}"))

    reg = policy.get("regression", {})
    if baseline is not None and reg.get("enabled", True):
        tol = reg.get("tolerance", {})
        base_m = baseline.metrics
        if base_m.get("phase1_hybrid_recall_at_k") is not None:
            drop = float(base_m["phase1_hybrid_recall_at_k"]) - float(
                m.get("phase1_hybrid_recall_at_k", 0)
            )
            if drop > tol.get("hybrid_recall_at_k", 0.05):
                violations.append(
                    _viol("regression.recall", f"recall dropped {drop:.3f} vs baseline")
                )
        if base_m.get("phase2_mean_faithfulness") is not None:
            drop = float(base_m["phase2_mean_faithfulness"]) - float(
                m.get("phase2_mean_faithfulness", 0)
            )
            if drop > tol.get("mean_faithfulness", 0.08):
                violations.append(
                    _viol("regression.faithfulness", f"faithfulness dropped {drop:.3f}")
                )

    if "public_corpus_naive_recall" in policy.get("advisory", {}).get("warn_only", []):
        advisories.append(
            _viol(
                "advisory.public_naive",
                "public naive recall is expected to be low under mock embedder",
                severity="warning",
            )
        )

    passed = not violations
    return PolicyOutcome(passed=passed, violations=violations, advisories=advisories)
