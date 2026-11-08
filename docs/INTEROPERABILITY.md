# Interoperability

SentinelRAG does **not** replace promptfoo, Ragas, or DeepEval. It imports their **scores** into a versioned evidence artifact and applies policy gates.

## Privacy boundary

Importers read numeric scores / named metrics only. They do **not** persist prompts, model responses, or traces into evidence JSON.

## CLI

```bash
sentinelrag-gate import promptfoo path/to/results.json -o build/artifact.json
sentinelrag-gate import ragas path/to/records.json --metric faithfulness --metric answer_relevancy -o build/artifact.json
sentinelrag-gate import deepeval path/to/report.json -o build/artifact.json

sentinelrag-gate run --baseline benchmarks/baseline_evidence.json
```

## Mapping (bridges)

| External | SentinelRAG key (when present) |
|----------|--------------------------------|
| faithfulness | `phase2_mean_faithfulness` |
| answer_relevancy | `phase2_mean_relevance` |
| context_recall / contextual_recall | `phase1_hybrid_recall_at_k` |

Details per tool: [integrations/promptfoo.md](integrations/promptfoo.md), [ragas.md](integrations/ragas.md), [deepeval.md](integrations/deepeval.md).

JSON Schema: [`schemas/evidence.schema.json`](../schemas/evidence.schema.json).
