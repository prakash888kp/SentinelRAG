# Benchmarks

Reproducible JSON (+ markdown tables) written by scripts under this directory.
**Never invent numbers** — regenerate with the matching `run_*.py` script.

| Artifact | Producer |
|----------|----------|
| `phase1_retrieval.json` | `run_phase1_retrieval.py` (CI / mock) |
| `phase1_retrieval_real.json` | `run_phase1_real.py` (real embedder + CE) |
| `phase2_eval.json` | `run_phase2_eval.py` |
| `phase3_trajectory.json` | `run_phase3_trajectory.py` |
| poison / red-team / Pareto | matching `run_*.py` scripts |

CI consumes the mock artifacts via `sentinelrag-gate`.
