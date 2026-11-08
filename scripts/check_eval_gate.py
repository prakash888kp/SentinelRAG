#!/usr/bin/env python3
"""Fail if phase1_retrieval.json metrics fall below config/eval_thresholds.yaml."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

from sentinelrag.paths import project_root


def main() -> int:
    root = project_root()
    report_path = root / "benchmarks" / "phase1_retrieval.json"
    thresholds_path = root / "config" / "eval_thresholds.yaml"
    if not report_path.is_file():
        print("Missing benchmarks/phase1_retrieval.json — run benchmarks/run_phase1_retrieval.py", file=sys.stderr)
        return 1
    report = json.loads(report_path.read_text(encoding="utf-8"))
    thresholds = yaml.safe_load(thresholds_path.read_text(encoding="utf-8"))
    phase1 = thresholds["phase1_retrieval"]
    failed = False
    for row in report["results"]:
        name = row["strategy"]
        floor = phase1[name]
        if row["recall_at_k"] < floor["recall_at_k_min"]:
            print(f"FAIL {name} recall@k {row['recall_at_k']} < {floor['recall_at_k_min']}")
            failed = True
        if row["mrr"] < floor["mrr_min"]:
            print(f"FAIL {name} mrr {row['mrr']} < {floor['mrr_min']}")
            failed = True
    if failed:
        return 1
    print("Eval gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
