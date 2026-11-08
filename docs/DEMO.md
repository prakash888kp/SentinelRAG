# 30–60 second demo (Gemini + real embedder + cross-encoder)

Live generation uses **Gemini** (`gemini-2.5-flash`). CI stays on mocks — no API keys required for gates.

## Prerequisites

- `GEMINI_API_KEY` in `.env`
- `uv sync --extra ml` (sentence-transformers / torch)
- Qdrant running (`docker compose up -d qdrant`)
- API started with real models (not the slim Compose API image alone)

```bash
docker compose up -d qdrant
docker compose stop api || true

# First time on a machine (downloads weights):
uv run python scripts/warmup_live_models.py

SENTINELRAG_VECTOR_STORE_BACKEND=qdrant \
SENTINELRAG_QDRANT_URL=http://127.0.0.1:6333 \
SENTINELRAG_EMBEDDING_MODEL=BAAI/bge-small-en-v1.5 \
SENTINELRAG_RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2 \
SENTINELRAG_LLM_PROVIDER=gemini \
SENTINELRAG_LLM_MODEL=gemini-2.5-flash \
uv run uvicorn sentinelrag.api.app:app --host 0.0.0.0 --port 8000
```

In another shell:

```bash
uv run python scripts/demo_60s.py
```

Cold start downloads models once; warm demos stay in the 30–60s window.

## What you see

1. `/health` — `llm_provider=gemini`, embedder + cross-encoder model ids  
2. `/ingest` — public corpus into Qdrant (skipped if already indexed)  
3. `/query?strategy=auto` — grounded Gemini answer + citations  

## CI vs demo

| Mode | Embedder | Reranker | LLM | Where |
|------|----------|----------|-----|--------|
| CI / `sentinelrag-gate` | mock | mock | mock | GitHub Actions |
| Live demo | `bge-small` | `ms-marco-MiniLM-L-6-v2` | Gemini 2.5 Flash | Your machine |

Phase map: [PHASES.md](PHASES.md)
