# SentinelRAG

Adaptive, attack-tested, eval-gated RAG. Phase 0 ships a runnable scaffold with MockLLM, FastAPI hello query, Qdrant Compose, and CI skeleton.

> Results-first tables, Pareto/ASR plots, and published numbers arrive in later phases from reproducible benchmark files — **none are invented here.**

## Quickstart

```bash
# install
uv sync --extra dev

# unit tests (offline, MockLLM)
uv run pytest

# one-command stack (Qdrant + API)
docker compose up --build -d
curl -s http://127.0.0.1:8000/health
curl -s -X POST http://127.0.0.1:8000/query -H "Content-Type: application/json" \
  -d '{"query":"What is SentinelRAG?"}'
```

Demo without Docker API image (API on host, Qdrant in Compose):

```bash
docker compose up -d qdrant
uv run uvicorn sentinelrag.api.app:app --host 127.0.0.1 --port 8000
```

## Azure-first hosting

Primary host is a stop/start Ubuntu VM + Docker Compose. See:

- `docs/CHAT_MEMORY.md` — durable decisions & Azure names
- `docs/adr/001-stack.md` — stack + hosting trade-offs
- `docs/azure/RUNBOOK.md` — how to finish VM create / deallocate
- `docs/azure/vm-bootstrap.sh` — Docker install on the VM

## Layout

```
src/sentinelrag/
  ingest/ retrieval/ router/ generation/ eval/ redteam/ observability/ api/
benchmarks/ docs/adr/ docs/azure/ .github/workflows/
```

## Phase 1 — mini corpus retrieval

- `data/mini_corpus/` — owned markdown docs; `data/mini_qrels.json` holds golden queries.
- Ingest: loaders, Pydantic metadata, fixed / semantic / contextual chunkers, no-op poisoning filter.
- Retrieval: MockEmbedder (CI), optional `sentence-transformers` via `uv sync --extra ml`, BM25, hybrid min-max fusion, MockReranker, in-memory and Qdrant stores.
- API: `POST /ingest` (corpus path or inline body), `POST /query?strategy=naive|hybrid`.
- Benchmark (generates real numbers locally):

```bash
uv run python benchmarks/run_phase1_retrieval.py
# writes benchmarks/phase1_retrieval.json and benchmarks/phase1_retrieval.md
```

Settings knobs include `SENTINELRAG_RETRIEVAL_TOP_K`, `SENTINELRAG_HYBRID_ALPHA`, `SENTINELRAG_CHUNK_SIZE`, and `SENTINELRAG_EMBEDDING_MODEL` (default `mock-embedder`).

## Phase status

| Phase | Status |
|-------|--------|
| 0 Scaffold + hello query | **Done locally** — Azure VM pending human finish |
| 1 Mini corpus + hybrid retrieval | **Done** — `benchmarks/phase1_retrieval.json` |
| 2 Golden set + LLM judge + CI gate | **Done** — `benchmarks/phase2_eval.json`, `POST /eval/run` |
| 3+ | Agentic retrieval, router, red team (planned) |

## Phase 2 — eval harness

- `data/golden_dataset.json` — seeded single/multi-hop items (`scripts/generate_golden_dataset.py`).
- Versioned judges under `src/sentinelrag/eval/judges/v1/`.
- `data/judge_calibration.json` — human labels for agreement reporting (MockJudge in CI).
- CI: `eval-gate` runs Phase 1 + Phase 2 and enforces `config/eval_thresholds.yaml`.

```bash
uv run python benchmarks/run_phase2_eval.py
uv run python scripts/check_eval_gate.py
```
