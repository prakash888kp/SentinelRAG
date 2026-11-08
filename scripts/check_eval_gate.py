#!/usr/bin/env python3
"""Fail if benchmark reports regress below config/eval_thresholds.yaml."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

from sentinelrag.paths import project_root


def _check_phase1(report: dict, thresholds: dict) -> bool:
    failed = False
    for row in report["results"]:
        name = row["strategy"]
        floor = thresholds[name]
        if row["recall_at_k"] < floor["recall_at_k_min"]:
            print(f"FAIL phase1 {name} recall@k {row['recall_at_k']} < {floor['recall_at_k_min']}")
            failed = True
        if row["mrr"] < floor["mrr_min"]:
            print(f"FAIL phase1 {name} mrr {row['mrr']} < {floor['mrr_min']}")
            failed = True
    return failed


def _check_phase2(report: dict, thresholds: dict) -> bool:
    failed = False
    checks = {
        "mean_recall_at_k": "mean_recall_at_k_min",
        "mean_faithfulness": "mean_faithfulness_min",
        "mean_relevance": "mean_relevance_min",
    }
    for metric, floor_key in checks.items():
        if report[metric] < thresholds[floor_key]:
            print(f"FAIL phase2 {metric} {report[metric]} < {thresholds[floor_key]}")
            failed = True
    agree = report["judge_agreement"]["within_0_2_rate"]
    floor = thresholds["judge_agreement_within_0_2_min"]
    if agree < floor:
        print(f"FAIL phase2 judge agreement {agree} < {floor}")
        failed = True
    return failed


def main() -> int:
    root = project_root()
    thresholds_path = root / "config" / "eval_thresholds.yaml"
    thresholds = yaml.safe_load(thresholds_path.read_text(encoding="utf-8"))
    failed = False

    phase1_path = root / "benchmarks" / "phase1_retrieval.json"
    if not phase1_path.is_file():
        print("Missing benchmarks/phase1_retrieval.json", file=sys.stderr)
        return 1
    failed |= _check_phase1(
        json.loads(phase1_path.read_text(encoding="utf-8")),
        thresholds["phase1_retrieval"],
    )

    phase2_path = root / "benchmarks" / "phase2_eval.json"
    if not phase2_path.is_file():
        print("Missing benchmarks/phase2_eval.json", file=sys.stderr)
        return 1
    failed |= _check_phase2(
        json.loads(phase2_path.read_text(encoding="utf-8")),
        thresholds["phase2_rag"],
    )

    if failed:
        return 1
    print("Eval gate passed (phase1 + phase2).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
