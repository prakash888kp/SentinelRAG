# Deployment

## Local Compose

```bash
docker compose up --build -d
curl -s http://127.0.0.1:8000/health
```

Slim Compose API uses mocks. For live Gemini + real models, run Qdrant from Compose and uvicorn on the host — see [DEMO.md](DEMO.md).

## Fresh Ubuntu Docker host

```bash
bash scripts/bootstrap-docker-host.sh
```

## Environment

| Variable | Purpose |
|----------|---------|
| `SENTINELRAG_LLM_PROVIDER` | `mock` (CI) or `gemini` (live) |
| `SENTINELRAG_LLM_MODEL` | e.g. `gemini-2.5-flash` |
| `GEMINI_API_KEY` | Live generation |
| `SENTINELRAG_EMBEDDING_MODEL` | `mock-embedder` or `BAAI/bge-small-en-v1.5` |
| `SENTINELRAG_RERANKER_MODEL` | `mock-reranker` or MiniLM CE |
| `SENTINELRAG_VECTOR_STORE_BACKEND` | `memory` or `qdrant` |
| `SENTINELRAG_QDRANT_URL` | e.g. `http://127.0.0.1:6333` |

Never commit `.env`. Template: `.env.example`.
