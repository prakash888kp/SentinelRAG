"""FastAPI /health and /query tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from sentinelrag.api.app import create_app
from sentinelrag.settings import Settings


def _client() -> TestClient:
    settings = Settings(env="test", llm_provider="mock", _env_file=None)
    return TestClient(create_app(settings))


def test_health() -> None:
    client = _client()
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["llm_provider"] == "mock"
    assert body["env"] == "test"
    assert "version" in body


def test_query_hello_grounded() -> None:
    client = _client()
    resp = client.post("/query", json={"query": "What is SentinelRAG?"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["provider"] == "mock"
    assert body["strategy"] == "hello_stub"
    assert "SentinelRAG" in body["answer"]
    assert len(body["citations"]) == 1
    assert body["citations"][0]["doc_id"] == "doc-hello-001"
    assert body["citations"][0]["chunk_id"] == "chunk-hello-001"


def test_query_rejects_empty() -> None:
    client = _client()
    resp = client.post("/query", json={"query": ""})
    assert resp.status_code == 422
