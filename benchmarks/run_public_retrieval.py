#!/usr/bin/env python3
"""Public corpus retrieval benchmark (OSS demo; mock embedder default)."""

from __future__ import annotations

import json

from sentinelrag.eval.phase1_retrieval import run_benchmark
from sentinelrag.paths import project_root, public_corpus_dir, public_qrels_path


def main() -> int:
    report = run_benchmark(
        corpus_dir=public_corpus_dir(),
        qrels_path=public_qrels_path(),
    )
    out = project_root() / "benchmarks" / "public_retrieval.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
