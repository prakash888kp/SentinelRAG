# SentinelRAG — Chat Memory (durable)

> Last updated: 2026-11-08. **Secrets never go here.**
> VM connection details live in private local notes / `.env` only — not in git.

## Project goal

Adaptive, attack-tested, eval-gated RAG platform: **ADAPTIVE** router/Pareto,
**SECURE** poisoning defenses, **EVALUATED** CI gates.

## Locked decisions

| Decision | Choice |
|----------|--------|
| Primary host | **Azure-first** optional VM + Docker Compose (Qdrant + API) |
| Package/tooling | Python 3.11+, **uv**, FastAPI, Pydantic v2, pytest, ruff, mypy strict |
| Vector store | **Qdrant** (Compose) |
| LLM in CI | **MockLLM** + **MockEmbedder** (offline gates) |
| OSS corpus | `data/public_corpus/` (20 original docs) + `data/mini_corpus/` for fast CI |
| Git | **Private** https://github.com/prakash888kp/SentinelRAG until maintainer flips public |
| Maintainer | PRAKASH KUMAR K (`prakash888kp`) — GitHub Issues only |
| License | MIT |

## Phase status

| Phase | Status |
|-------|--------|
| 0–6 | **Done** — v0.1.0, triple-gate CI |
| OSS launch pack | **Done** — CONTRIBUTING, SECURITY, public corpus, PyPI metadata |
| Phase 7 supply-chain gate | **Done** — `sentinelrag-gate`, SARIF/JUnit, poison v1, composite Action |

## OSS positioning

**Triple-gate adaptive RAG** — unlike eval-only tools (rag-ci, raggate, RAGAS plugins),
this repo ships the **app + three CI gates** (retrieval, RAG quality, poison defenses).

See `docs/COMPARISON.md` and `docs/SECURITY_AUDIT.md`.

## Azure (high level)

- Runbook: `docs/azure/RUNBOOK.md`, bootstrap: `docs/azure/vm-bootstrap.sh`
- Deploy script: `scripts/azure_vm_deploy.py` (reads `AZURE_VM_*` from local `.env`)
- Cost: deallocate VM when idle

## Test results (reference)

```
pytest: 47+ passed, coverage ~85%
GitHub Actions: ci, eval-gate, redteam-gate green on master
```

## Azure real-model track (locked)

| Item | Choice |
|------|--------|
| LLM | **Gemini** `gemini-2.5-flash` (2.0-flash shut down) |
| Embedder | `BAAI/bge-small-en-v1.5` via `--extra ml` |
| Reranker (demo) | `mock-reranker` (fast 60s); optional CE later |
| Vector | Qdrant on VM Compose |
| Demo | `scripts/demo_60s.py` (~11s warm on Azure) |
| Real bench | `benchmarks/phase1_retrieval_real.json` |

## Next action

1. Rotate Gemini key if it ever appeared in logs/URLs
2. Say **ok to public** when ready
3. Deallocate VM when idle

## Session log

- 2026-11-08: Azure real-model track — ml extras, real bge recall@1.0, Gemini 2.5 demo 11s, gate+pytest on VM.
