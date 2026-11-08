# Benchmarks

All numbers in README and evidence must come from scripts under `benchmarks/`.

| Script | Output | Mode |
|--------|--------|------|
| `run_phase1_retrieval.py` | `phase1_retrieval.json` | Mock (CI) |
| `run_phase1_real.py` | `phase1_retrieval_real.json` | Real embedder + CE |
| `run_public_retrieval.py` | `public_retrieval.json` | Public corpus |
| `run_phase2_eval.py` | `phase2_eval.json` | Judges + golden |
| `run_phase3_trajectory.py` | `phase3_trajectory.json` | Agentic |
| `run_pareto.py` | Pareto plot + JSON | Cost / latency |
| `run_redteam_sweep.py` | `asr_vs_alpha.json` | Poison ASR |
| `run_poison_benchmark_v1.py` | `poison_benchmark_v1.json` | Defense story |
| `run_hygiene_scan.py` | hygiene evidence | Corpus scan |

```bash
uv run python benchmarks/run_phase1_retrieval.py
uv run sentinelrag-gate collect   # → benchmarks/baseline_evidence.json
```
