# Live demo — reproduce the README recording

The README GIF ([assets/demo-live.gif](assets/demo-live.gif)) is a **terminal recording** of:

1. `sentinelrag-gate run --refresh` (offline, mock)  
2. `scripts/demo_60s.py` against a warm API (Gemini + bge-small + MiniLM CE)

## Reproduce (live path)

```bash
docker compose up -d qdrant
docker compose stop api || true
uv sync --extra ml
uv run python scripts/warmup_live_models.py

SENTINELRAG_VECTOR_STORE_BACKEND=qdrant \
SENTINELRAG_QDRANT_URL=http://127.0.0.1:6333 \
SENTINELRAG_EMBEDDING_MODEL=BAAI/bge-small-en-v1.5 \
SENTINELRAG_RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2 \
SENTINELRAG_LLM_PROVIDER=gemini \
SENTINELRAG_LLM_MODEL=gemini-2.5-flash \
uv run uvicorn sentinelrag.api.app:app --host 0.0.0.0 --port 8000
```

```bash
# requires GEMINI_API_KEY in .env
uv run python scripts/demo_60s.py
```

## Refresh the GIF

```bash
uv pip install pillow   # or any env with Pillow
uv run python scripts/render_demo_gif.py
```

| Mode | Embedder | Reranker | LLM |
|------|----------|----------|-----|
| CI / gate | mock | mock | mock |
| Live recording | `bge-small` | MiniLM CE | Gemini 2.5 Flash |
