"""FastAPI /health, /ingest, and /query tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from sentinelrag.api.app import create_app
from sentinelrag.settings import Settings


def _client() -> TestClient:
    settings = Settings(
        env="test",
        llm_provider="mock",
        vector_store_backend="memory",
        _env_file=None,
    )
    return TestClient(create_app(settings))


def test_health() -> None:
    client = _client()
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["llm_provider"] == "mock"
    assert body["llm_model"] == "mock-llm"
    assert body["embedding_model"] == "mock-embedder"
    assert body["reranker_model"] == "mock-reranker"
    assert body["env"] == "test"
    assert "version" in body
    assert "index_ready" in body


def test_ingest_mini_corpus() -> None:
    client = _client()
    resp = client.post("/ingest", json={})
    assert resp.status_code == 200
    body = resp.json()
    assert body["chunks_indexed"] >= 5


def test_query_retrieval_hybrid() -> None:
    client = _client()
    client.post("/ingest", json={})
    resp = client.post(
        "/query",
        json={"query": "What is SentinelRAG?"},
        params={"strategy": "hybrid"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["provider"] == "mock"
    assert body["strategy"] == "hybrid"
    assert "SentinelRAG" in body["answer"]
    assert len(body["citations"]) >= 1


def test_query_naive_strategy() -> None:
    client = _client()
    client.post("/ingest", json={})
    resp = client.post(
        "/query",
        json={"query": "recall at k"},
        params={"strategy": "naive"},
    )
    assert resp.status_code == 200
    assert resp.json()["strategy"] == "naive"


def test_eval_run_offline() -> None:
    client = _client()
    resp = client.post("/eval/run")
    assert resp.status_code == 200
    body = resp.json()
    assert body["n_golden_items"] == 5
    assert body["judge_prompt_version"] == "v1"


def test_query_rejects_empty() -> None:
    client = _client()
    resp = client.post("/query", json={"query": ""})
    assert resp.status_code == 422
