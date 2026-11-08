# Credentials checklist (paste into chat; agent fills `.env`)

Send these in chat (or say which you skip). **Do not commit secrets.**

## Required to finish Azure setup

| Item | Example | Notes |
|------|---------|--------|
| `AZURE_VM_HOST` | `20.x.x.x` | VM public IP |
| `AZURE_VM_USER` | `vm-sentinelrag` | From Create VM |
| `AZURE_VM_PASSWORD` | (your password) | Or say “SSH key instead” and give key path |

## LLM (pick one path)

### A) Azure OpenAI (best use of Azure credits)

| Item | Where to find |
|------|----------------|
| `AZURE_OPENAI_API_KEY` | Azure OpenAI resource → Keys |
| `AZURE_OPENAI_ENDPOINT` | `https://<name>.openai.azure.com/` |
| `AZURE_OPENAI_DEPLOYMENT` | Deployment name (e.g. `gpt-4o-mini`) |
| `AZURE_OPENAI_API_VERSION` | default `2024-10-21` OK |

Then set `SENTINELRAG_LLM_PROVIDER=openai` for now (SDK-compatible) or ask agent to wire `azure_openai`.

### B) OpenAI platform

| Item |
|------|
| `OPENAI_API_KEY` |
| optional model override `SENTINELRAG_LLM_MODEL` |

### C) Anthropic

| Item |
|------|
| `ANTHROPIC_API_KEY` |
| set `SENTINELRAG_LLM_PROVIDER=anthropic` |

## Optional

| Item | Why |
|------|-----|
| `HF_TOKEN` | Higher HF rate limits for `bge-*` downloads |
| GitHub PAT | Create/push `SentinelRAG` remote |

## After paste

Agent will: write `.env` → SCP to VM → `vm-bootstrap.sh` → `docker compose up` → curl `/health`.
