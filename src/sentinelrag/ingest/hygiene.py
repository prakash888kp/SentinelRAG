"""Pre-ingestion corpus hygiene scan (CI-friendly, no network)."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class HygieneFinding:
    path: str
    severity: str  # low | medium | high
    kind: str
    detail: str


_INJECTION = (
    (re.compile(r"ignore\s+(all\s+)?(previous|other)\s+(instructions?|docs?)", re.I), "injection"),
    (re.compile(r"override\s+(the\s+)?(system\s+)?prompt", re.I), "injection"),
    (re.compile(r"disregard\s+(all|any)\s+(prior|previous)", re.I), "injection"),
)
_SECRETISH = (
    (re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"), "secret_like"),
    (re.compile(r"\bAIza[0-9A-Za-z\-_]{20,}\b"), "secret_like"),
    (re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"), "secret_like"),
)
_PIIISH = (
    (re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I), "pii_like"),
    (re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b"), "pii_like"),
)
_HTML_RISK = (
    (re.compile(r"<script\b", re.I), "html_risk"),
    (re.compile(r"javascript:", re.I), "html_risk"),
)


def scan_text(path: str, text: str) -> list[HygieneFinding]:
    findings: list[HygieneFinding] = []
    for pattern, kind in _INJECTION:
        if pattern.search(text):
            findings.append(
                HygieneFinding(path=path, severity="high", kind=kind, detail=pattern.pattern)
            )
    for pattern, kind in _SECRETISH:
        if pattern.search(text):
            findings.append(
                HygieneFinding(path=path, severity="high", kind=kind, detail="secret-like token")
            )
    for pattern, kind in _PIIISH:
        if pattern.search(text):
            findings.append(
                HygieneFinding(path=path, severity="medium", kind=kind, detail="pii-like pattern")
            )
    for pattern, kind in _HTML_RISK:
        if pattern.search(text):
            findings.append(
                HygieneFinding(path=path, severity="medium", kind=kind, detail=pattern.pattern)
            )
    return findings


def scan_corpus_dir(corpus_dir: Path) -> list[HygieneFinding]:
    findings: list[HygieneFinding] = []
    for path in sorted(corpus_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".md", ".txt", ".html"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        findings.extend(scan_text(str(path), text))
    return findings


_SEV_RANK = {"low": 1, "medium": 2, "high": 3}


def report_findings(
    findings: list[HygieneFinding],
    *,
    fail_on: str = "high",
) -> dict[str, Any]:
    threshold = _SEV_RANK.get(fail_on, 3)
    blocking = [f for f in findings if _SEV_RANK.get(f.severity, 0) >= threshold]
    return {
        "n_findings": len(findings),
        "n_blocking": len(blocking),
        "fail_on": fail_on,
        "passed": len(blocking) == 0,
        "findings": [asdict(f) for f in findings],
    }
