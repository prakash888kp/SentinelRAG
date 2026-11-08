# ADR-001: Stack and Azure-first hosting

- Status: Accepted
- Date: 2026-11-08

## Context

SentinelRAG needs a portfolio-grade RAG stack that is offline-testable in CI, runnable with one Compose command, and hostable without relying on the developer's local OMEN as the primary machine. The user locked **Azure-first** hosting with ~$100 credits and asked that git stay local until push is approved.

## Decision

### Application stack

| Concern | Choice | Rationale |
|---------|--------|-----------|
| Language | Python 3.11+ | Ecosystem fit for RAG/eval tooling |
| Packaging | **uv** | Fast, lockfile-friendly, CI-simple |
| API | FastAPI | Typed routes, OpenAPI, async-ready |
| Config | Pydantic v2 Settings | Validated env-driven knobs; no secrets in tree |
| Quality | pytest, ruff, mypy strict | Non-negotiable quality bar |
| Vectors | **Qdrant** via Docker Compose | Mature, local/cloud parity, sparse later |
| LLM (CI/default) | **MockLLM** | Deterministic, free, offline |
| LLM (prod path) | Provider interface: Anthropic / OpenAI / Bedrock | Sketched in Phase 0; clients not called in CI |
| Reranker / embedder | Behind interfaces | Real models optional; CI uses mocks |
| Observability | OpenTelemetry (later phases) | Interfaces stubbed early |

### Hosting: Azure-first

**Primary host:** a cheap stop/start **Ubuntu VM** (B2s-class, 2 vCPU / 8 GB) running Docker Compose (Qdrant + API). Develop/mirror code under `D:\AI Engg\SentinelRAG` for Cursor, sync to the VM for Compose verification. Cursor Remote SSH is the preferred editor attachment once the VM is Running.

**Cost habit:** deallocate the VM when idle. MockLLM in CI so credits are not burned by model APIs.

## Alternatives considered

| Option | Pros | Cons | Why not primary |
|--------|------|------|-----------------|
| Local OMEN + Docker Desktop | Fastest iteration, $0 infra, GPU for Phase 1 table | User locked Azure-first; Windows Docker friction | Secondary / fallback only |
| GitHub Codespaces | Near-identical Compose/git loop | Recurring Codespaces cost; less control of long-lived Qdrant | Good online alternative, not chosen |
| Notebooks (Colab/Kaggle) | Free GPU bursts | No Compose/daemon workflow; poor repo/CI loop | One-off GPU only |
| Always-free Azure only (Container Apps, AI Search Free, App Service F1) | Low cost | Not enough for real Qdrant Compose + durable Docker host | Complementary later, not Phase 0 host |
| Managed Qdrant Cloud + serverless API | Less VM ops | Extra vendor; still need a compute story for ingest/eval | Optional later |

## Consequences

- Phase 0 must ship Compose + offline + CI that pass **without** Azure if the portal path is blocked.
- SSH keys and `.env` live outside git; CHAT_MEMORY documents names/paths only.
- Idle VM risk is real — document deallocate steps in CHAT_MEMORY and Azure runbooks.
- Phase 1 published benchmarks still require an explicit real-embedder run (VM or local); CI stays Mock.

## References

- `docs/CHAT_MEMORY.md`
- `docs/azure/` runbooks
