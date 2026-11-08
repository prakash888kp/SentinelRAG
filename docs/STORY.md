# The SentinelRAG story

## Act I — The silent regression

Your team ships a RAG feature. Hybrid retrieval looks fine in a notebook. A PR tweaks chunk size.
Recall drops. Nobody notices until users complain.

## Act II — The second failure mode

You add evals. Faithfulness gates catch bad answers. But a poisoned doc slips through ingest because
metadata looked “trusted.” Retrieval surfaces it. The model obliges.

## Act III — Supply-chain gates

SentinelRAG treats RAG like supply chain:

1. **Retrieve** with measurable recall (offline, mock-safe CI).
2. **Answer** with versioned judges and golden sets (`data/golden.jsonl`).
3. **Defend** at ingest, after retrieval, and in red-team probes.

One command bundles the evidence auditors expect:

```bash
uv run sentinelrag-gate run --refresh
```

Outputs land in `.sentinelrag/gate/`:

- `evidence.json` — versioned metrics bundle
- `junit.xml` — test reporters
- `sarif.json` — security scanners
- `summary.md` — human PR summary

## Act IV — Your pipeline, your adapter

Drop an `adapter.py` with `collect_metrics()` (see `examples/adapter_template.py`) and point
policy at your numbers. The reference app proves the gates; the CLI ships the discipline.

## Act V — Poison demo

```bash
uv run sentinelrag-gate demo-poison
```

Shows raw retrieval attack surface vs ingest blocks vs post-retrieval trim — the narrative hook
for security-minded teams.

## Epilogue — Anchor the baseline

```bash
uv run sentinelrag-gate collect
```

Commit the evidence under `.sentinelrag/gate/` (or your policy’s artifact path) so the next PR fails loudly if recall, faithfulness, or poison defenses slip.
