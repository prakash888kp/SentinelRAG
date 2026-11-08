# RAG security controls → CI probes

Maps industry RAG security guidance to **automated probes in this repository**.
Each probe is offline unless you opt into live models.

| Control theme | CI probe | Artifact |
|---------------|----------|----------|
| Poisoned document retrieval | `redteam-gate` + `poison_benchmark_v1` | `benchmarks/asr_vs_alpha.json`, `poison_benchmark_v1.json` |
| Ingest-time poison rejection | ingest defense fraction | `defense_probe_blocked_fraction` |
| Indirect prompt / lexical injection | `LexicalAnomalyFilter` tests | `tests/test_redteam.py` |
| Metadata / trust tampering | `MetadataTrustFilter` + attack samples | red-team harness |
| Post-retrieval containment | `PostRetrievalTrim` | `post_retrieval_mean_asr` in poison v1 |
| Retrieval regression | phase1 + public corpus benchmarks | `phase1_retrieval.json` |
| Answer grounding regression | phase2 eval gate | `phase2_eval.json` |
| Unified audit trail | `sentinelrag-gate run` | `.sentinelrag/gate/evidence.json`, SARIF |

Run the full mapped suite:

```bash
uv run sentinelrag-gate run --refresh
```

Add probes by extending `benchmarks/` and `config/gate_policy.yaml` — keep policy as the single
source of pass/fail semantics.
