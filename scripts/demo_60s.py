#!/usr/bin/env python3
"""30–60s live demo: health → ingest (if needed) → auto query via Gemini + real embedder.

Run on a machine with Qdrant up and ``uv sync --extra ml`` + GEMINI_API_KEY set.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def _req(method: str, url: str, body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode()
    headers = {"Content-Type": "application/json"} if body is not None else {}
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=120) as resp:
        return json.loads(resp.read().decode())


def main() -> int:
    base = os.environ.get("SENTINELRAG_DEMO_URL", "http://127.0.0.1:8000").rstrip("/")
    t0 = time.perf_counter()
    print("=== SentinelRAG 60s demo ===\n")
    try:
        health = _req("GET", f"{base}/health")
    except urllib.error.URLError as exc:
        print(f"API not reachable at {base}: {exc}", file=sys.stderr)
        print("Start stack: docker compose up -d qdrant && uv run uvicorn …", file=sys.stderr)
        return 1
    print(
        f"1) health: {health.get('status')} version={health.get('version')} "
        f"llm={health.get('llm_provider')}/{health.get('llm_model')} "
        f"embed={health.get('embedding_model')} rerank={health.get('reranker_model')} "
        f"index_ready={health.get('index_ready')}"
    )

    if not health.get("index_ready"):
        print("2) ingest public corpus …")
        corpus = str(Path("data/public_corpus").resolve())
        ing = _req("POST", f"{base}/ingest", {"corpus_path": corpus})
        print(f"   ingested chunks={ing.get('chunks_indexed', ing)}")
    else:
        print("2) index already ready — skip ingest")

    print("3) query strategy=auto …")
    q = _req(
        "POST",
        f"{base}/query?strategy=auto",
        {
            "query": (
                "What ingest-time defenses and CI gates does SentinelRAG use "
                "against corpus poisoning?"
            )
        },
    )
    answer = str(q.get("answer", ""))[:500]
    print(f"   answer: {answer}")
    print(f"   strategy={q.get('strategy')} provider={q.get('provider')}")
    cites = q.get("citations") or []
    print(f"   citations={len(cites)}")
    for c in cites[:3]:
        print(f"     - {c.get('chunk_id')}: {str(c.get('snippet', ''))[:80]}")
    elapsed = time.perf_counter() - t0
    print(f"\nDone in {elapsed:.1f}s")
    return 0 if elapsed < 120 else 0


if __name__ == "__main__":
    raise SystemExit(main())
