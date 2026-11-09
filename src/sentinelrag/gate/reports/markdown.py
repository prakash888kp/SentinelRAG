"""Human-readable PR / step summary."""

from __future__ import annotations

from pathlib import Path

from sentinelrag.gate.evidence import EvidenceBundle
from sentinelrag.gate.policy import PolicyOutcome


def render_summary(outcome: PolicyOutcome, evidence: EvidenceBundle) -> str:
    status = "PASSED" if outcome.passed else "FAILED"
    chunker = evidence.chunker_config or {}
    lines = [
        f"# SentinelRAG supply-chain gate — {status}",
        "",
        "## Provenance",
        f"- binding mode: **{evidence.binding_mode}**",
        f"- app revision: **{evidence.app_revision or evidence.commit or 'unknown'}**",
        (
            "- chunker: "
            f"**{chunker.get('strategy', '?')}** "
            f"size={chunker.get('chunk_size', '?')} "
            f"overlap={chunker.get('chunk_overlap', '?')}"
        ),
        "",
        "## Retrieval",
        f"- hybrid recall@k: **{evidence.metrics.get('phase1_hybrid_recall_at_k')}**",
        f"- hybrid MRR: **{evidence.metrics.get('phase1_hybrid_mrr')}**",
        "",
        "## Answer quality",
        f"- faithfulness: **{evidence.metrics.get('phase2_mean_faithfulness')}**",
        f"- relevance: **{evidence.metrics.get('phase2_mean_relevance')}**",
        "",
        "## Security probes",
        "- ingest defense blocked: "
        f"**{evidence.security_probes.get('ingest_defense_blocked_fraction')}**",
        "",
    ]
    poison = evidence.security_probes.get("poison_benchmark_v1")
    if poison:
        lines.extend(
            [
                "## Poison benchmark v1",
                f"- ingest block rate: **{poison.get('ingest_block_rate')}**",
                f"- post-retrieval ASR (with trim): **{poison.get('post_retrieval_mean_asr')}**",
                "",
            ]
        )
    if outcome.violations:
        lines.append("### Violations")
        for v in outcome.violations:
            lines.append(f"- `{v['rule']}`: {v['message']}")
        lines.append("")
    if outcome.advisories:
        lines.append("### Advisories")
        for w in outcome.advisories:
            lines.append(f"- {w['message']}")
        lines.append("")
    return "\n".join(lines)


def write_markdown(outcome: PolicyOutcome, evidence: EvidenceBundle, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_summary(outcome, evidence), encoding="utf-8")
