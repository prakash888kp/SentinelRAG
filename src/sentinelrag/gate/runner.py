"""Run benchmarks, collect evidence, enforce policy, emit reports."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from sentinelrag.gate.evidence import EvidenceBundle, collect_evidence
from sentinelrag.gate.policy import PolicyOutcome, evaluate_policy, load_policy
from sentinelrag.gate.reports.junit import write_junit
from sentinelrag.gate.reports.markdown import write_markdown
from sentinelrag.gate.reports.sarif import write_sarif
from sentinelrag.paths import project_root


@dataclass(frozen=True, slots=True)
class GateResult:
    outcome: PolicyOutcome
    evidence: EvidenceBundle
    out_dir: Path


def _run_script(rel: str) -> None:
    root = project_root()
    script = root / rel
    if not script.is_file():
        return
    subprocess.run([sys.executable, str(script)], cwd=root, check=True)


def refresh_benchmarks() -> None:
    """Regenerate all benchmark artifacts used by the unified gate."""
    for rel in (
        "benchmarks/run_phase1_retrieval.py",
        "benchmarks/run_public_retrieval.py",
        "benchmarks/run_phase2_eval.py",
        "benchmarks/run_redteam_sweep.py",
        "benchmarks/run_poison_benchmark_v1.py",
    ):
        _run_script(rel)


def load_baseline(path: Path) -> EvidenceBundle | None:
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    bundle = EvidenceBundle()
    bundle.schema = str(data.get("schema", bundle.schema))
    bundle.metrics = dict(data.get("metrics", {}))
    bundle.security_probes = dict(data.get("security_probes", {}))
    return bundle


def run_gate(
    *,
    policy_path: Path | None = None,
    out_dir: Path | None = None,
    baseline_path: Path | None = None,
    refresh: bool = False,
) -> GateResult:
    root = project_root()
    out = out_dir or (root / ".sentinelrag" / "gate")
    out.mkdir(parents=True, exist_ok=True)

    if refresh:
        refresh_benchmarks()

    evidence = collect_evidence(root=root)
    baseline = load_baseline(baseline_path or (root / "benchmarks" / "baseline_evidence.json"))
    policy = load_policy(policy_path)
    outcome = evaluate_policy(evidence, policy, baseline=baseline)

    evidence.passed = outcome.passed
    evidence.violations = outcome.violations
    evidence.write_json(out / "evidence.json")
    write_junit(outcome, evidence, out / "junit.xml")
    write_sarif(outcome, out / "sarif.json")
    write_markdown(outcome, evidence, out / "summary.md")

    import os

    from sentinelrag.gate.reports.markdown import render_summary

    gh_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if gh_summary:
        Path(gh_summary).write_text(render_summary(outcome, evidence), encoding="utf-8")

    return GateResult(outcome=outcome, evidence=evidence, out_dir=out)
