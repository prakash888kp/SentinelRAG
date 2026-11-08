# 30–60 second demo (Gemini + real embedder)

## Prerequisites

- `GEMINI_API_KEY` in `.env`
- `uv sync --extra ml` (sentence-transformers / torch)
- Qdrant running (`docker compose up -d qdrant`)
- API with real models (not the slim Compose image alone)

```bash
export PATH="$HOME/.local/bin:$PATH"
docker compose up -d qdrant
# stop slim api if it holds :8000
docker compose stop api || true
SENTINELRAG_VECTOR_STORE_BACKEND=qdrant \
SENTINELRAG_QDRANT_URL=http://127.0.0.1:6333 \
SENTINELRAG_EMBEDDING_MODEL=BAAI/bge-small-en-v1.5 \
SENTINELRAG_RERANKER_MODEL=mock-reranker \
SENTINELRAG_LLM_PROVIDER=gemini \
SENTINELRAG_LLM_MODEL=gemini-2.0-flash \
uv run uvicorn sentinelrag.api.app:app --host 0.0.0.0 --port 8000
```

In another shell:

```bash
uv run python scripts/demo_60s.py
```

First run downloads `bge-small` (~hours once; later demos stay under a minute after warmup).

## What you see

1. `/health` — version, `llm_provider=gemini`
2. `/ingest` — public corpus into Qdrant  
3. `/query?strategy=auto` — grounded answer + citations  

## CI vs demo

| Mode | Embedder | LLM | Where |
|------|----------|-----|--------|
| CI / `sentinelrag-gate` | mock | mock | GitHub Actions |
| Live demo / Azure track | `bge-small` | Gemini | Your VM |
