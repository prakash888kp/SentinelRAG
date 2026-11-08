# SentinelRAG — Chat Memory (durable)

> Last updated: 2026-11-08. Obsidian MCP unavailable — this file is the source of truth across chats.
> **Secrets never go here.** Resource names, RG, region, and how-to-connect only.

## Project goal

Adaptive, attack-tested, eval-gated RAG platform proving: ADAPTIVE (router/Pareto), SECURE (poisoning defenses), EVALUATED (CI gates).

## Locked decisions

| Decision | Choice |
|----------|--------|
| Primary host | **Azure-first** (not local OMEN as primary) |
| Budget | ~$100 Azure credits (portal showed ₹19,045.75 remaining as of 2026-11-08; expires ~2026-12-07) |
| Runtime topology | Stop/start Ubuntu VM + Docker Compose (Qdrant + API) |
| Package/tooling | Python 3.11+, **uv**, FastAPI, Pydantic v2, pytest, ruff, mypy strict |
| Vector store | **Qdrant** (Compose on VM) |
| LLM in CI | **MockLLM** deterministic; real providers sketched only |
| Phase 1 published table | Real embedder on VM/local run; CI stays Mock embedder |
| Phase 1 corpus | Authored mini-corpus; public dataset in Phase 2 |
| Git | Small conventional commits locally; **do not push** until user says ready |
| License | MIT |

## Azure topology (target)

```
[Cursor on Windows] --SSH--> [Azure Ubuntu VM]
                               ├── Docker Compose
                               │     ├── qdrant
                               │     └── sentinelrag-api
                               └── /opt/sentinelrag (code mirror)
```

### Resources (fill as created)

| Resource | Value | Notes |
|----------|-------|-------|
| Subscription | (portal default / student+credits) | Check portal |
| Resource group | `rg-sentinelrag` | Create/reuse |
| Region | TBD at create time | Prefer Central India / South India / East US |
| VM name | `vm-sentinelrag` | Ubuntu 22.04/24.04, B2s-class |
| Public IP | TBD | Document when Running |
| NSG | SSH 22 inbound | Restrict later if possible |
| SSH user | `azureuser` (typical) | Confirm after create |
| SSH private key path | `C:\Users\praka\.ssh\sentinelrag_azure` (outside git) | Never commit |
| Connect | `ssh -i ~/.ssh/sentinelrag_azure azureuser@<PUBLIC_IP>` | |
| Cost control | **Deallocate** VM when idle | Stop ≠ deallocate; disk still bills |

### Credentials locations (no secrets in repo)

- Azure portal: Edge session (MFA as needed)
- SSH private key: user `.ssh` only; `.gitignore` covers `*.pem`, `id_*`
- App secrets: `.env` on VM / local (from `.env.example`); never committed

## Phase status

| Phase | Status |
|-------|--------|
| **0** Scaffold, MockLLM, `/health` `/query`, Compose, CI skeleton, ADR-001 | **IN PROGRESS** |
| 1 Ingest + retrieval + first table | NOT STARTED — wait for user **continue** |
| 2+ | NOT STARTED |

## Workspace paths

- Cursor-visible mirror: `D:\AI Engg\SentinelRAG`
- Personal agent store copy: `...\u211987363\files\SentinelRAG_CHAT_MEMORY.md`
- Azure runbooks: `docs/azure/`

## Next action

1. Finish Azure RG + cheap Ubuntu VM (or document blocker).
2. Complete Phase 0 repo + green tests.
3. **STOP** — wait for user message `continue` before Phase 1.

## Open risks (living)

- Azure portal computer-use / MFA may block VM create.
- Idle VM burns credits if not deallocated.
- B2s availability varies by region under student/credit SKUs.
- SSH from agent shell may be restricted; fallback: `docs/azure/vm-bootstrap.sh` for user.

## Session log

- 2026-11-08: Locked Azure-first; Phase 0 only; memory docs created; Azure portal confirmed open in Edge with credits.
