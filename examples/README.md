# Examples

| Path | Purpose |
|------|---------|
| `adapter_template.py` | Drop-in `collect_metrics()` for foreign RAG pipelines |
| `gate/candidate_summary.json` | Minimal evidence blob for gate / compare demos |
| `import_promptfoo/` | Sample promptfoo results → `sentinelrag-gate import promptfoo` |
| `import_ragas/` | Sample Ragas records → `sentinelrag-gate import ragas` |
| `import_deepeval/` | Sample DeepEval report → `sentinelrag-gate import deepeval` |

```bash
uv run sentinelrag-gate import promptfoo examples/import_promptfoo/results.json -o build/from-promptfoo.json
uv run sentinelrag-gate import ragas examples/import_ragas/evaluation-result-records.json \
  --metric faithfulness --metric answer_relevancy -o build/from-ragas.json
uv run sentinelrag-gate import deepeval examples/import_deepeval/report.json -o build/from-deepeval.json
```
