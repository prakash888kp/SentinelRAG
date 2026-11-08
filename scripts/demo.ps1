# SentinelRAG local demo (Windows). MockLLM + in-memory index — no secrets required.
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host "== sync dev deps =="
uv sync --extra dev

Write-Host "== unit tests =="
uv run pytest -q

Write-Host "== benchmarks (offline) =="
uv run python benchmarks/run_phase1_retrieval.py
uv run python benchmarks/run_phase2_eval.py
uv run python benchmarks/run_phase3_trajectory.py
uv run python benchmarks/run_pareto.py
uv run python benchmarks/run_redteam_sweep.py
uv run python scripts/check_eval_gate.py
uv run python scripts/check_redteam_gate.py

Write-Host "== API smoke (in-memory) =="
$env:SENTINELRAG_VECTOR_STORE_BACKEND = "memory"
$env:SENTINELRAG_LLM_PROVIDER = "mock"
$proc = Start-Process -PassThru -NoNewWindow uv `
    -ArgumentList "run", "uvicorn", "sentinelrag.api.app:app", "--host", "127.0.0.1", "--port", "8000"
Start-Sleep -Seconds 3
try {
    Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" | ConvertTo-Json
    $body = @{ query = "What is SentinelRAG?"; strategy = "auto" } | ConvertTo-Json
    Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/query" `
        -ContentType "application/json" -Body $body | ConvertTo-Json -Depth 5
} finally {
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
}

Write-Host "Demo complete."
