# Poison benchmark v1

Named, reproducible security scorecard for the reference RAG stack (mock embedder).

## Metrics

| Metric | Meaning |
|--------|---------|
| `ingest_block_rate` | Share of canonical attack chunks rejected at ingest |
| `post_retrieval_mean_asr` | Attack success after post-retrieval trim |

## Regenerate

```bash
uv run python benchmarks/run_poison_benchmark_v1.py
```

## Gate thresholds

See `config/gate_policy.yaml` → `absolute.poison_benchmark_v1`.

Committed results: `benchmarks/poison_benchmark_v1.json`.
