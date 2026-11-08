# Metrics

| Metric | Meaning | Direction | Typical source |
|--------|---------|-----------|----------------|
| `phase1_hybrid_recall_at_k` | Relevant docs in top-k hybrid | Higher | Phase 1 / public / Ragas bridge |
| `phase1_hybrid_mrr` | Mean reciprocal rank | Higher | Phase 1 |
| `phase1_hybrid_hit_rate_at_k` | Query has ≥1 relevant hit | Higher | Phase 1 |
| `phase1_hybrid_latency_ms_mean` | Retrieval wall time | Lower | Phase 1 |
| `phase2_mean_faithfulness` | Answer grounded in context | Higher | Phase 2 / imports |
| `phase2_mean_relevance` | Answer addresses question | Higher | Phase 2 / imports |
| `phase2_mean_recall_at_k` | Context covers gold | Higher | Phase 2 |
| `ingest_defense_blocked_fraction` | Poison probes blocked at ingest | Higher | Red-team |
| `poison_benchmark_v1.*` | Ingest block + post-trim ASR | See policy | Poison v1 |

Policy floors live in `config/gate_policy.yaml` and `config/eval_thresholds.yaml`.
Schema: `schemas/evidence.schema.json`.
