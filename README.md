# SentinelRAG

[![CI](https://github.com/prakash888kp/SentinelRAG/actions/workflows/ci.yml/badge.svg)](https://github.com/prakash888kp/SentinelRAG/actions/workflows/ci.yml)
[![Supply-chain gate](https://github.com/prakash888kp/SentinelRAG/actions/workflows/supply-chain-gate.yml/badge.svg)](https://github.com/prakash888kp/SentinelRAG/actions/workflows/supply-chain-gate.yml)
[![PyPI](https://img.shields.io/pypi/v/sentinelrag.svg)](https://pypi.org/project/sentinelrag/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**RAG evaluation and security CI for retrieval-augmented generation.**  
Fail the build when **retrieval recall**, **answer grounding**, or **corpus poison / hygiene defenses** regress — with evidence, JUnit, and SARIF. Ships an adaptive FastAPI + Qdrant reference stack.

Searchable keywords: RAG CI · retrieval regression testing · LLM security · corpus poisoning · hygiene scan · hybrid BM25 · cross-encoder rerank · agentic RAG · GitHub Actions gate.

**Author:** PRAKASH KUMAR K ([@prakash888kp](https://github.com/prakash888kp)) · **Support:** [GitHub Issues](https://github.com/prakash888kp/SentinelRAG/issues)

[Story](docs/STORY.md) · [Demo](docs/DEMO.md) · [Phases](docs/PHASES.md) · [OWASP map](docs/OWASP_RAG_CI_MAP.md) · [Comparison](docs/COMPARISON.md)

---

## Install

```bash
pip install sentinelrag
# or
uv add sentinelrag
```

From source:

```bash
git clone https://github.com/prakash888kp/SentinelRAG.git
cd SentinelRAG
uv sync --extra dev
cp .env.example .env
```

---

## Out of the box

### Offline / CI (no API keys)

```bash
uv run pytest
uv run sentinelrag-gate run --refresh
uv run sentinelrag-gate demo-poison
uv run sentinelrag-gate scan data/public_corpus --fail-on high
```

### Live 30–60s demo (Gemini + real embedder + cross-encoder)

See **[docs/DEMO.md](docs/DEMO.md)**. After Qdrant + API are warm:

```bash
uv sync --extra ml
uv run python scripts/warmup_live_models.py   # once
uv run python scripts/demo_60s.py
```

| Command | What it does |
|---------|----------------|
| `sentinelrag-gate run` | Policy gate → `evidence.json`, JUnit, SARIF, summary |
| `sentinelrag-gate collect` | Anchor baseline evidence |
| `sentinelrag-gate compare` | Metric deltas between evidence files |
| `sentinelrag-gate scan` | Pre-ingest hygiene (injection / secret-like / PII-like) |
| `sentinelrag-gate demo-poison` | Poison ASR story (ingest + post-retrieval) |

Artifacts: `.sentinelrag/gate/` · Policy: `config/gate_policy.yaml`

### Drop into any GitHub repo

```yaml
- uses: prakash888kp/SentinelRAG/.github/actions/sentinelrag-gate@v0.2.0
  with:
    refresh: "true"
```

---

## What problem this solves

Teams building RAG systems need:

1. **Golden-set retrieval regression** (recall / hit-rate / MRR) separate from generation  
2. **CI that fails on quality drops** vs a committed baseline  
3. **Pre-ingest hygiene** before vectors land in the index  
4. **Poison / indirect injection probes** in the same pipeline as eval  
5. **Audit artifacts** (JSON evidence, JUnit, SARIF) — not log spam  

SentinelRAG ships that stack **offline by default** (MockLLM / MockEmbedder).

```mermaid
flowchart LR
  CORPUS[Corpus] --> HYG[Hygiene scan]
  HYG --> PROV[Provenance manifest]
  PROV --> ING[Ingest defenses]
  ING --> RET[Naive / Hybrid / Agentic]
  RET --> TRIM[Post-retrieval trim]
  TRIM --> GEN[Generation]
  RET & GEN & HYG --> GATE[sentinelrag-gate]
  GATE --> ART[Evidence · JUnit · SARIF]
```

---

## Results

**CI / mock** (`benchmarks/phase1_retrieval.json`, seed 42): hybrid recall@k **1.0**

**Real embedder** (`benchmarks/phase1_retrieval_real.json`, `bge-small-en-v1.5`):

| Corpus | naive recall@5 | hybrid recall@5 |
|--------|---------------:|----------------:|
| mini | **1.0** | **1.0** |
| public (20 docs) | **1.0** | **1.0** |

Also: poison v1, hygiene, provenance, phase2 mock judges in CI. Live path: **Gemini 2.5 Flash** + `bge-small` + MiniLM cross-encoder ([DEMO](docs/DEMO.md)).

---

## Layout

```
src/sentinelrag/
  api/           FastAPI service
  ingest/        loaders, chunking, hygiene, provenance, filters
  retrieval/     BM25, hybrid, agentic, stores
  router/        complexity + cost policy
  eval/          metrics, judges, golden I/O, latency
  redteam/       attacks, defenses, post-retrieval, harness
  gate/          evidence, policy, CLI, SARIF/JUnit
  generation/    MockLLM + Gemini (live)
  observability/ cost + OTel
benchmarks/      reproducible JSON + plots
config/          eval_thresholds.yaml · gate_policy.yaml
data/            mini_corpus · public_corpus · golden.jsonl
```

---

## API demo

```bash
docker compose up --build -d
curl -s http://127.0.0.1:8000/health
curl -s -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What is triple-gate RAG?", "strategy":"auto"}'
```

Host bootstrap (Docker Engine on a fresh Ubuntu box): `scripts/bootstrap-docker-host.sh`

---

## Docs

[CONTRIBUTING](CONTRIBUTING.md) · [SECURITY](SECURITY.md) · [CHANGELOG](CHANGELOG.md) · [PHASES](docs/PHASES.md) · [DEMO](docs/DEMO.md) · [COMPARISON](docs/COMPARISON.md) · [POISON_BENCHMARK_v1](docs/POISON_BENCHMARK_v1.md)

## License

MIT
