# Ragas → SentinelRAG

Export records without shipping sample text into the gate:

```bash
# result.to_pandas().to_json("records.json", orient="records")
uv run sentinelrag-gate import ragas records.json \
  --metric faithfulness --metric answer_relevancy \
  --producer-version 0.2.x \
  -o build/sentinelrag-artifact.json
```

Fixture: `examples/import_ragas/evaluation-result-records.json`.
