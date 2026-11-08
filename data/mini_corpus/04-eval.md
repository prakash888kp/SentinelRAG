# Evaluation Metrics

The eval package implements recall at k and mean reciprocal rank (MRR) for retrieval
benchmarks. Phase 1 runs these metrics on `data/mini_qrels.json` against the mini
corpus with a fixed random seed so JSON and Markdown benchmark tables are reproducible.

Future phases add LLM-as-judge and attack-success metrics; Phase 1 focuses on
retrieval quality only.
