#!/usr/bin/env python3
"""Scan tracked files for accidental secret patterns (CI-safe)."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

# Patterns that should never appear in committed files (values, not key names alone).
PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("google_api_key", re.compile(r"AIza[0-9A-Za-z\-_]{20,}")),
    ("openai_key", re.compile(r"sk-[a-zA-Z0-9]{20,}")),
    ("github_pat", re.compile(r"ghp_[a-zA-Z0-9]{20,}")),
    ("private_ipv4_vm", re.compile(r"\b20\.83\.171\.151\b")),
]


def tracked_files(root: Path) -> list[Path]:
    out = subprocess.check_output(
        ["git", "ls-files"],
        cwd=root,
        text=True,
    )
    return [root / line.strip() for line in out.splitlines() if line.strip()]


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    failures: list[str] = []
    for path in tracked_files(root):
        if path.name == ".env":
            failures.append(f"TRACKED .env: {path.relative_to(root)}")
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for label, pattern in PATTERNS:
            if pattern.search(text):
                failures.append(f"{label} in {path.relative_to(root)}")
    if failures:
        for line in failures:
            print(f"SECRET SCAN FAIL: {line}", file=sys.stderr)
        return 1
    print("Secret scan passed (tracked files).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
