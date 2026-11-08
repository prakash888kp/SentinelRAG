"""Document provenance digests for integrity checks."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_manifest(corpus_dir: Path) -> dict[str, Any]:
    entries: list[dict[str, str]] = []
    for path in sorted(corpus_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".md", ".txt"}:
            continue
        rel = path.relative_to(corpus_dir).as_posix()
        entries.append({"path": rel, "sha256": file_sha256(path)})
    digest = hashlib.sha256(
        "|".join(f"{e['path']}:{e['sha256']}" for e in entries).encode()
    ).hexdigest()
    return {"corpus": corpus_dir.name, "files": entries, "manifest_sha256": digest}


def write_manifest(corpus_dir: Path, out: Path) -> dict[str, Any]:
    payload = build_manifest(corpus_dir)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def verify_manifest(corpus_dir: Path, manifest_path: Path) -> dict[str, Any]:
    expected = json.loads(manifest_path.read_text(encoding="utf-8"))
    actual = build_manifest(corpus_dir)
    ok = expected.get("manifest_sha256") == actual["manifest_sha256"]
    return {
        "passed": ok,
        "expected": expected.get("manifest_sha256"),
        "actual": actual["manifest_sha256"],
    }
