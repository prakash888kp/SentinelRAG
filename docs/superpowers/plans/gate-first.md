# Plan: gate-first

1. `uv sync --extra dev`  
2. `uv run pytest -q`  
3. `uv run sentinelrag-gate run --refresh`  
4. Only then enable Gemini / `--extra ml` for DEMO.md  
