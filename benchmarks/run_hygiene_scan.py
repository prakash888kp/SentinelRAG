#!/usr/bin/env python3
"""Scan mini + public corpora for pre-ingest hygiene findings."""

from __future__ import annotations

import json

from sentinelrag.ingest.hygiene import report_findings, scan_corpus_dir
from sentinelrag.ingest.provenance import write_manifest
from sentinelrag.paths import mini_corpus_dir, project_root, public_corpus_dir


def main() -> int:
    root = project_root()
    findings = scan_corpus_dir(mini_corpus_dir()) + scan_corpus_dir(public_corpus_dir())
    report = report_findings(findings, fail_on="high")
    # Educational attack phrases in our own corpus are expected; only secrets block CI.
    secret_findings = [f for f in report["findings"] if f["kind"] == "secret_like"]
    report["n_blocking"] = len(secret_findings)
    report["passed"] = len(secret_findings) == 0
    report["policy"] = "block_secret_like_only"
    out = root / "benchmarks" / "hygiene_report.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    write_manifest(mini_corpus_dir(), root / "benchmarks" / "corpus_manifest.json")
    print(f"Wrote {out}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
