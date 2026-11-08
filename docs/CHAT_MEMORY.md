# SentinelRAG — Chat Memory (durable)

> Last updated: 2026-11-08. Obsidian MCP unavailable — this file is the source of truth across chats.
> **Secrets never go here.** Resource names, RG, region, and how-to-connect only.

## Project goal

Adaptive, attack-tested, eval-gated RAG platform proving: ADAPTIVE (router/Pareto), SECURE (poisoning defenses), EVALUATED (CI gates).

## Locked decisions

| Decision | Choice |
|----------|--------|
| Primary host | **Azure-first** (not local OMEN as primary) |
| Budget | Azure credits (~₹19,045.75 remaining as of 2026-11-08; expires ~2026-12-07) |
| Runtime topology | Stop/start Ubuntu VM + Docker Compose (Qdrant + API) |
| Package/tooling | Python 3.11+, **uv**, FastAPI, Pydantic v2, pytest, ruff, mypy strict |
| Vector store | **Qdrant** (Compose on VM) |
| LLM in CI | **MockLLM** deterministic; real providers sketched only |
| Phase 1 published table | Real embedder on VM/local run; CI stays Mock embedder |
| Phase 1 corpus | Authored mini-corpus; public dataset in Phase 2 |
| Git | **Private GitHub** https://github.com/prakash888kp/SentinelRAG (`master`) |
| Runtime config | `.env` (gitignored) production-style models; secrets filled when user pastes |
| Compose | `env_file: .env`; forces `SENTINELRAG_QDRANT_URL=http://qdrant:6333` |
| License | MIT |

## Azure topology (target)

```
[Cursor on Windows] --SSH--> [Azure Ubuntu VM]
                               ├── Docker Compose
                               │     ├── qdrant
                               │     └── sentinelrag-api
                               └── ~/sentinelrag (code mirror)
```

### Resources (as of Phase 0 end)

| Resource | Value | Notes |
|----------|-------|-------|
| Subscription | Azure subscription 1 | Portal account `prakash888kp@outlook.com` |
| Resource group | `rg-sentinelrag` | **Not created yet** — finish in portal |
| Region | Prefer Central/South India; East US tried | D2s_v3 unavailable in eastus for this sub |
| VM name | `vm-sentinelrag` | Target Ubuntu 24.04, B2s-class |
| Public IP | `20.83.171.151` | vm-sentinelrag; SSH password auth |
| LLM (runtime) | **Gemini** `gemini-2.0-flash` via `GEMINI_API_KEY` | Azure OpenAI fields still empty |
| Deploy | `scripts/azure_vm_deploy.py` | Docker + Compose up on VM |
| NSG | SSH 22 inbound | Restrict later if possible |
| SSH user | `azureuser` | Typical portal default |
| SSH private key path | `C:\Users\praka\.ssh\sentinelrag_azure` (outside git) | Never commit |
| Connect | `ssh -i ~/.ssh/sentinelrag_azure azureuser@<PUBLIC_IP>` | |
| Cost control | **Deallocate** VM when idle | Stop ≠ deallocate; disk still bills |

### Credentials locations (no secrets in repo)

- Azure portal: Edge session (MFA as needed)
- SSH private key: user `.ssh` only; `.gitignore` covers keys
- App secrets: `.env` on VM / local (from `.env.example`); never committed

### Azure bootstrap status

**BLOCKED for agent computer-use.** Portal Create VM Basics opened with Ubuntu 24.04 selected; size picker / Create new RG / Continue clicks did not stick after repeated attempts. No `az` CLI on PATH. See `docs/azure/RUNBOOK.md` for the exact human finish steps + `vm-bootstrap.sh`.

## Phase status

| Phase | Status |
|-------|--------|
| 0 | Done — VM live, Compose up |
| 1 | Done — `benchmarks/phase1_retrieval.json` |
| 2 | Done — `phase2_eval.json`, `eval-gate` CI |
| 3 | Done — agentic multi-hop, `phase3_trajectory.json`, OTel |
| 4 | Done — router/policy, `pareto_points.json` |
| 5 | Done — red-team harness, `asr_vs_alpha.json`, `redteam-gate`, ADR-002 |
| 6 | Done — **v0.1.0**, README table, CHANGELOG, `scripts/demo.ps1` |

## What was built (Phase 0)

- Repo at `D:\AI Engg\SentinelRAG` (Cursor-visible mirror)
- Package layout: ingest/retrieval/router/generation/eval/redteam/observability/api + benchmarks/docs
- Settings (Pydantic v2), MockLLM + provider sketches, FastAPI hello path
- `docker-compose.yml` (Qdrant + API), Dockerfile, `.env.example`, MIT license
- GitHub Actions: `ci.yml` (ruff/mypy/pytest), `eval.yml` / `redteam.yml` placeholders (pass)
- ADR-001 + Azure runbook + `vm-bootstrap.sh`
- Local git commits (7) on `master` — **not pushed**

## Test results (local Windows, uv + CPython 3.14)

```
ruff: pass
mypy strict (src/sentinelrag): pass
pytest: 47 passed, coverage ~85%
```

Docker daemon was not confirmed running during Phase 0; Compose verification deferred to Azure VM (or local Docker Desktop once up).

## Workspace paths

- Cursor mirror: `D:\AI Engg\SentinelRAG`
- Personal agent store: `...\u211987363\files\SentinelRAG_CHAT_MEMORY.md`
- Azure runbooks: `docs/azure/`

## Open risks

1. Azure VM not provisioned — human must finish Create VM (B2s + RG) per RUNBOOK.
2. Credit SKU/region availability (D2s_v3 blocked in East US; B2s may need region hunting).
3. Idle VM burns credits if not **deallocated**.
4. No `az` CLI installed — portal-only until winget install.
5. Computer-use unreliable on Azure SPA primary buttons.
6. Local Docker daemon may be stopped — Compose demo needs Docker or the Azure VM.

## Next action

1. Pull `master` and watch CI (`ci`, `eval-gate`, `redteam-gate`) on GitHub.
2. Optional: `uv run python scripts/azure_vm_deploy.py` after green CI to refresh VM.
3. Rotate any secrets pasted in chat; keep `.env` out of git.

## Session log

- 2026-11-08: Phases 0–2 shipped earlier; Phases 3–6 completed autonomously (agentic, Pareto, red-team, v0.1.0 polish), pushed to `master`, tag `v0.1.0`.
