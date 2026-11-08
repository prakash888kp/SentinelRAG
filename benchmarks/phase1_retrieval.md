# Phase 1 retrieval benchmark

| Field | Value |
| --- | --- |
| embedding_model | `mock-embedder` |
| corpus_hash | `008f44c7f5078bdf` |
| seed | 42 |
| retrieval_top_k | 5 |
| hybrid_alpha | 0.5 |

| strategy | recall@k | MRR |
| --- | ---: | ---: |
| naive | 0.8333 | 0.3667 |
| hybrid | 1.0000 | 0.5139 |
