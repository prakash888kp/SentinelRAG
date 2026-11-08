"""Public OSS corpus qrels align with ingested chunk ids."""

from __future__ import annotations

import json

from sentinelrag.ingest.pipeline import IndexState, ingest_corpus_dir
from sentinelrag.paths import public_corpus_dir, public_qrels_path
from sentinelrag.settings import settings_without_dotenv


def test_public_qrels_chunk_ids_exist() -> None:
    cfg = settings_without_dotenv(embedding_model="mock-embedder", vector_store_backend="memory")
    state = IndexState()
    ingest_corpus_dir(public_corpus_dir(), state, settings=cfg)
    qrels = json.loads(public_qrels_path().read_text(encoding="utf-8"))["queries"]
    missing: list[str] = []
    for item in qrels:
        for cid in item["relevant_chunk_ids"]:
            if cid not in state.chunks:
                missing.append(cid)
    assert not missing, f"missing chunks: {missing}"
