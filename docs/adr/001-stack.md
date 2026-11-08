# ADR-001: Stack and hosting

- Status: Accepted
- Date: 2026-11-08

## Context

SentinelRAG needs an offline-testable RAG stack for CI, a one-command Compose demo, and optional self-hosting on any Docker host.

## Decision

### Application stack

| Concern | Choice | Rationale |
|---------|--------|-----------|
| Language | Python 3.11+ | Ecosystem fit for RAG / eval tooling |
| Packaging | **uv** + hatchling | Fast lockfile + PyPI wheel |
| API | FastAPI | Typed routes, OpenAPI |
| Config | Pydantic v2 Settings | Validated env-driven knobs; no secrets in tree |
| Quality | pytest, ruff, mypy strict | Non-negotiable quality bar |
| Vectors | **Qdrant** via Docker Compose | Local / cloud parity |
| LLM (CI) | **MockLLM** | Deterministic, free, offline |
| LLM (live demo) | **Gemini** (`gemini-2.5-flash`) | Real grounded answers without Azure OpenAI |
| Embedder / reranker | Interfaces + optional `--extra ml` | CI uses mocks; live uses bge-small + MiniLM CE |
| Observability | OpenTelemetry hooks | Cost + tracing stubs |

### Hosting

**Default:** `docker compose up` on a developer laptop or any Ubuntu Docker host (`scripts/bootstrap-docker-host.sh`). CI never needs a GPU or API keys.

## Alternatives considered

| Option | Why not primary |
|--------|-----------------|
| Notebook-only (Colab) | Weak Compose / CI loop |
| Managed vector DB only | Still needs a gate + API story |
| Azure OpenAI as required LLM | Live track locked to Gemini; other providers remain optional stubs |

## Consequences

- CI stays mock-safe forever.
- Live demos document Gemini + real models in `docs/DEMO.md`.
- Secrets stay in `.env` (gitignored).
