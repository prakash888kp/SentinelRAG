# Benchmarks

Committed JSON (+ plots) from reproducible scripts. Do not invent numbers.

| Artifact | Script |
|----------|--------|
| `phase1_retrieval.json` | `run_phase1_retrieval.py` |
| `phase1_retrieval_real.json` | `run_phase1_real.py` |
| `public_retrieval.json` | `run_public_retrieval.py` |
| `phase2_eval.json` | `run_phase2_eval.py` |
| `phase3_trajectory.json` | `run_phase3_trajectory.py` |
| `pareto_points.json` / `pareto_plot.png` / `leaderboard.json` | `run_pareto.py` · `export_leaderboard.py` |
| `asr_vs_alpha.json` / `asr_vs_alpha.png` | `run_redteam_sweep.py` |
| `poison_benchmark_v1.json` | `run_poison_benchmark_v1.py` |
| `hygiene_report.json` | `run_hygiene_scan.py` |
| `corpus_manifest.json` | provenance during gate/hygiene |
| `baseline_evidence.json` | `sentinelrag-gate collect` |

```bash
uv run python benchmarks/run_phase1_retrieval.py
uv run sentinelrag-gate collect
```
