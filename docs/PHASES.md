# Phase checklist

Live generation uses **Gemini** (`gemini-2.5-flash`). CI stays fully mock.

| Phase | What shipped | Proof in repo |
|------:|--------------|---------------|
| **0** | FastAPI health / ingest / query, MockLLM hello path | `tests/test_api.py`, `tests/test_llm.py` |
| **1** | Naive + hybrid + BM25 fusion + (mock/real) rerank; recall/MRR/hit-rate | `tests/test_retrieval*.py`, `benchmarks/run_phase1_*.py`, `phase1_retrieval*.json` |
| **2** | Golden RAG eval + judges + CI eval-gate | `tests/test_phase2_eval.py`, `tests/test_judge.py`, `.github/workflows/eval-gate.yml` |
| **3** | Agentic multi-hop + trajectory metrics | `tests/test_phase3_agentic.py`, `benchmarks/run_phase3_trajectory.py` |
| **4** | Complexity router + Pareto cost/latency | `tests/test_router.py`, `benchmarks/run_pareto.py` |
| **5** | Poison / red-team attacks + defenses + gate | `tests/test_redteam.py`, `benchmarks/run_redteam_sweep.py`, `redteam-gate.yml` |
| **6** | Observability (cost + OTel hooks) + OSS packaging | `tests/test_observability.py`, CONTRIBUTING / SECURITY / public corpus |
| **7** | Supply-chain gate CLI (evidence, SARIF/JUnit, hygiene, poison demo) | `tests/test_gate*.py`, `sentinelrag-gate`, `supply-chain-gate.yml` |

## Live demo models

| Layer | Model |
|-------|--------|
| Embedder | `BAAI/bge-small-en-v1.5` |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| LLM | `gemini-2.5-flash` (`GEMINI_API_KEY`) |
| Store | Qdrant |

```bash
uv run pytest -q
uv run sentinelrag-gate run --refresh
uv run python scripts/warmup_live_models.py
uv run python scripts/demo_60s.py
```
