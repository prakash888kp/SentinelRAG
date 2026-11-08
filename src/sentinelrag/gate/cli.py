"""CLI: unified supply-chain gate and demos."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sentinelrag.gate.evidence import collect_evidence
from sentinelrag.gate.runner import refresh_benchmarks, run_gate
from sentinelrag.paths import project_root
from sentinelrag.redteam.harness import run_redteam


def _cmd_run(args: argparse.Namespace) -> int:
    result = run_gate(
        policy_path=Path(args.policy) if args.policy else None,
        out_dir=Path(args.out) if args.out else None,
        baseline_path=Path(args.baseline) if args.baseline else None,
        refresh=args.refresh,
    )
    if not result.outcome.passed:
        for v in result.outcome.violations:
            print(f"FAIL {v['rule']}: {v['message']}", file=sys.stderr)
        return 1
    print(f"Gate passed; evidence in {result.out_dir}")
    return 0


def _cmd_collect(args: argparse.Namespace) -> int:
    _ = args
    refresh_benchmarks()
    evidence = collect_evidence()
    out = project_root() / "benchmarks" / "baseline_evidence.json"
    evidence.write_json(out)
    print(f"Wrote {out}")
    return 0


def _cmd_compare(args: argparse.Namespace) -> int:
    candidate = json.loads(Path(args.candidate).read_text(encoding="utf-8"))
    baseline = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    deltas: dict[str, float] = {}
    for key, val in candidate.get("metrics", {}).items():
        base = baseline.get("metrics", {}).get(key)
        if base is not None:
            deltas[key] = float(val) - float(base)
    print(json.dumps({"deltas": deltas}, indent=2))
    return 0


def _cmd_scan(args: argparse.Namespace) -> int:
    from sentinelrag.ingest.hygiene import report_findings, scan_corpus_dir

    findings = scan_corpus_dir(Path(args.path))
    report = report_findings(findings, fail_on=args.fail_on)
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


def _cmd_demo_poison(args: argparse.Namespace) -> int:
    _ = args
    print("=== SentinelRAG poison story (offline) ===\n")
    report = run_redteam(alpha=0.5)
    print(f"Ingest defense blocked fraction: {report['defense_probe_blocked_fraction']}")
    print(f"Mean retrieval ASR (no post-trim): {report['mean_retrieval_asr']}")
    poison_path = project_root() / "benchmarks" / "poison_benchmark_v1.json"
    if not poison_path.is_file():
        refresh_benchmarks()
    poison = json.loads(poison_path.read_text(encoding="utf-8"))
    print(f"Ingest block rate (probes): {poison['ingest_block_rate']}")
    print(f"Post-retrieval ASR (with trim): {poison['post_retrieval_mean_asr']}")
    print("\nRun `sentinelrag-gate run` to enforce policy on these numbers.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sentinelrag-gate", description="SentinelRAG CI gate")
    sub = parser.add_subparsers(dest="cmd", required=True)

    run_p = sub.add_parser("run", help="Evaluate policy and emit SARIF/JUnit")
    run_p.add_argument("--policy", default="config/gate_policy.yaml")
    run_p.add_argument("--baseline", default="benchmarks/baseline_evidence.json")
    run_p.add_argument("--out", default=".sentinelrag/gate")
    run_p.add_argument("--refresh", action="store_true", help="Regenerate benchmarks first")
    run_p.set_defaults(func=_cmd_run)

    col = sub.add_parser("collect", help="Refresh benchmarks and anchor baseline evidence")
    col.set_defaults(func=_cmd_collect)

    cmp_p = sub.add_parser("compare", help="Print metric deltas between evidence files")
    cmp_p.add_argument("candidate")
    cmp_p.add_argument("baseline")
    cmp_p.set_defaults(func=_cmd_compare)

    demo = sub.add_parser("demo-poison", help="Print poison before/after story")
    demo.set_defaults(func=_cmd_demo_poison)

    scan_p = sub.add_parser("scan", help="Pre-ingest hygiene scan on a corpus directory")
    scan_p.add_argument("path", help="Corpus directory")
    scan_p.add_argument("--fail-on", default="high", choices=["low", "medium", "high"])
    scan_p.set_defaults(func=_cmd_scan)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
