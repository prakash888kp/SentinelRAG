# SentinelRAG

![SentinelRAG](docs/assets/sentinelrag-hero.jpg)

[![CI](https://github.com/prakash888kp/SentinelRAG/actions/workflows/ci.yml/badge.svg)](https://github.com/prakash888kp/SentinelRAG/actions/workflows/ci.yml)
[![Supply-chain gate](https://github.com/prakash888kp/SentinelRAG/actions/workflows/supply-chain-gate.yml/badge.svg)](https://github.com/prakash888kp/SentinelRAG/actions/workflows/supply-chain-gate.yml)
[![PyPI](https://img.shields.io/pypi/v/sentinelrag)](https://pypi.org/project/sentinelrag/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Triple-gate RAG for CI.** Retrieval can look fine in a notebook while a PR quietly tanks recall, ships an ungrounded answer, or lets a poisoned doc into the index. SentinelRAG treats those as **three separate checkpoints** — and fails the build when any one of them slips — with evidence your existing CI already understands (JSON, JUnit, SARIF).

`pip install sentinelrag` · `sentinelrag-gate` CLI · FastAPI + Qdrant reference app · offline mocks in CI · optional Gemini live path

---

## Three checkpoints before merge

| Checkpoint | Catches | How |
|------------|---------|-----|
| **Retrieve** | Silent recall / hit-rate / MRR drops | Golden corpora + hybrid (+ optional cross-encoder) |
| **Ground** | Answers that ignore the context | Versioned judges on a golden set |
| **Defend** | Junk / injection / poison at ingest | Hygiene scan, ingest filters, red-team ASR probes |

Foreign eval scores (promptfoo, Ragas, DeepEval) can feed the same evidence schema — SentinelRAG does not replace those tools; it **unifies their numbers with its own gates**.

![Pipeline](docs/assets/pipeline.png)

```mermaid
flowchart TB
  subgraph before_merge [Before the PR merges]
    A[Corpus change] --> B{Retrieve OK?}
    B -->|no| X[Fail CI]
    B -->|yes| C{Grounded OK?}
    C -->|no| X
    C -->|yes| D{Poison / hygiene OK?}
    D -->|no| X
    D -->|yes| E[Attach evidence · JUnit · SARIF]
  end
```

The **gate does not need** Gemini, a GPU, or Qdrant. The FastAPI app is there when you want a live stack with citations.

```mermaid
flowchart LR
  subgraph live [Optional live stack]
    API["/health /ingest /query"] --> V[(Qdrant)]
    API --> M[bge-small + MiniLM]
    API --> G[Gemini]
  end
  subgraph ci [Always-on CI]
    CLI[sentinelrag-gate] --> OUT[.sentinelrag/gate/]
  end
```

---

## See it query a corpus

![Live preview](docs/assets/live-preview.png)

![Animated walkthrough](docs/assets/demo-live.gif)

Walkthrough: [docs/DEMO.md](docs/DEMO.md)

---

## Install & run the gate

```bash
pip install sentinelrag
# from source:
# uv sync --extra dev

uv run sentinelrag-gate run --refresh
uv run sentinelrag-gate demo-poison
uv run sentinelrag-gate scan data/public_corpus --fail-on high
```

Outputs: `.sentinelrag/gate/` · Policy: `config/gate_policy.yaml`

**Plug into GitHub Actions**

```yaml
- uses: prakash888kp/SentinelRAG/.github/actions/sentinelrag-gate@v0.2.1
  with:
    refresh: "true"
```

**Bring scores from other evaluators**

```bash
uv run sentinelrag-gate import promptfoo examples/import_promptfoo/results.json -o build/art.json
uv run sentinelrag-gate import ragas examples/import_ragas/evaluation-result-records.json \
  --metric faithfulness --metric answer_relevancy -o build/art.json
uv run sentinelrag-gate import deepeval examples/import_deepeval/report.json -o build/art.json
```

Recipes: [CI cookbook](docs/CI_COOKBOOK.md) · Mapping: [Interoperability](docs/INTEROPERABILITY.md)

---

## In the box

- **App** — FastAPI ingest/query, hybrid + agentic retrieval, complexity router  
- **Gate** — policy YAML, baselines, SARIF/JUnit, composite Action  
- **Security loop** — hygiene, provenance SHA, poison benchmark v1  
- **Interop** — promptfoo / Ragas / DeepEval → `sentinelrag-evidence-v1`  
- **Schemas & examples** — [`schemas/`](schemas/) · [`examples/`](examples/)

---

## Benchmarks

Committed JSON + plots in [`benchmarks/`](benchmarks/). Scripts: [docs/BENCHMARK.md](docs/BENCHMARK.md).

### At a glance

| Gate | Headline |
|------|----------|
| **Retrieve** | Hybrid recall@5 **1.0** (mock CI + real `bge-small` on mini & public) |
| **Ground** | Faithfulness **0.83** · relevance **1.0** · trajectory recall **1.0** |
| **Defend** | Ingest defenses block **100%** of probes · post-trim poison ASR **0.33** (from 1.0 raw) |
| **Hygiene** | Scan **passed** · 0 findings |

### Quality vs cost

Hybrid hits full recall cheaper than agentic; naive is cheapest but weaker.

![Strategy trade-off — quality vs cost](docs/assets/benchmark-pareto.png)

| Strategy | recall@k | USD / query | latency |
|----------|---------:|------------:|--------:|
| naive | 0.83 | 0.00005 | ~14 ms |
| **hybrid** | **1.0** | 0.0002 | ~5 ms |
| agentic | **1.0** | 0.0012 | ~85 ms |

### Poison probes vs hybrid α

Ingest defenses stay at **1.0** blocked. Raw retrieval ASR only drops when α → dense (1.0).

![Poison ASR vs hybrid alpha](docs/assets/benchmark-asr.png)

| | |
|--|--|
| Poison v1 ingest block rate | **0.67** |
| After post-retrieval trim | ASR **0.33** |

### Retrieval detail

| Corpus | Embedder | naive@5 | hybrid@5 |
|--------|----------|--------:|---------:|
| Mini (CI) | mock | 0.83 | **1.0** |
| Public (CI) | mock | 0.25 | **1.0** |
| Mini | `bge-small` | **1.0** | **1.0** |
| Public | `bge-small` | **1.0** | **1.0** |

Raw files: `phase1_retrieval*.json`, `phase2_eval.json`, `phase3_trajectory.json`, `pareto_points.json`, `asr_vs_alpha.json`, `poison_benchmark_v1.json`, `hygiene_report.json`, `baseline_evidence.json`.

---

## Dig deeper

[Architecture](docs/ARCHITECTURE.md) · [Metrics](docs/METRICS.md) · [Benchmarks](docs/BENCHMARK.md) · [Deployment](docs/DEPLOYMENT.md) · [Poison v1](docs/POISON_BENCHMARK_v1.md) · [OWASP map](docs/OWASP_RAG_CI_MAP.md) · [Story](docs/STORY.md) · [Phases](docs/PHASES.md) · [Comparison](docs/COMPARISON.md) · [Changelog](CHANGELOG.md)

---

## License

[MIT](LICENSE) · [NOTICE](NOTICE)
