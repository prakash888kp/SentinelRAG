#!/usr/bin/env python3
"""Azure-first real-model track: ml deps, real embed benchmarks, API+Gemini e2e, 60s demo."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import paramiko
except ImportError:
    print("uv sync --extra dev (paramiko)", file=sys.stderr)
    raise SystemExit(1) from None

sys.path.insert(0, str(Path(__file__).resolve().parent))
from azure_vm_deploy import load_env, run_ssh  # noqa: E402


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    env = load_env(repo / ".env")
    host, user, password = (
        env.get("AZURE_VM_HOST", ""),
        env.get("AZURE_VM_USER", ""),
        env.get("AZURE_VM_PASSWORD", ""),
    )
    if not all([host, user, password]):
        print("Missing AZURE_VM_*", file=sys.stderr)
        return 1
    if not env.get("GEMINI_API_KEY"):
        print("Missing GEMINI_API_KEY in .env", file=sys.stderr)
        return 1

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"SSH {user}@{host}")
    client.connect(hostname=host, username=user, password=password, timeout=60)
    remote = f"/home/{user}/sentinelrag"
    try:
        transport = client.get_transport()
        assert transport is not None
        sftp = paramiko.SFTPClient.from_transport(transport)
        assert sftp is not None

        # Sync critical files (not full tree — faster)
        for rel in (
            "pyproject.toml",
            "uv.lock",
            "src",
            "data",
            "benchmarks",
            "scripts/demo_60s.py",
            "scripts/azure_real_model_track.py",
            "docker-compose.yml",
            ".env",
            "config",
        ):
            local = repo / rel
            if local.is_file():
                rpath = f"{remote}/{rel}"
                run_ssh(client, f"mkdir -p {Path(rpath).parent.as_posix()}")
                sftp.put(str(local), rpath)
            elif local.is_dir():
                for path in local.rglob("*"):
                    if path.is_dir() or "__pycache__" in path.parts:
                        continue
                    rel_p = path.relative_to(repo).as_posix()
                    rpath = f"{remote}/{rel_p}"
                    run_ssh(client, f"mkdir -p {Path(rpath).parent.as_posix()}")
                    sftp.put(str(path), rpath)

        path_export = "export PATH=$HOME/.local/bin:$PATH"
        soft_prefixes = ("pkill ",)
        soft_contains = ("docker compose stop api",)
        steps = [
            f"cd {remote} && (command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh)",
            f"{path_export} && cd {remote} && uv sync --extra dev --extra ml",
            f"cd {remote} && sudo docker compose stop api || true",
            f"cd {remote} && sudo docker compose up -d qdrant",
            "pkill -f 'uvicorn sentinelrag.api.app' || true",
            (
                f"bash -lc '{path_export} && cd {remote} && "
                "nohup env SENTINELRAG_VECTOR_STORE_BACKEND=qdrant "
                "SENTINELRAG_QDRANT_URL=http://127.0.0.1:6333 "
                "SENTINELRAG_EMBEDDING_MODEL=BAAI/bge-small-en-v1.5 "
                "SENTINELRAG_RERANKER_MODEL=mock-reranker "
                "SENTINELRAG_LLM_PROVIDER=gemini "
                "SENTINELRAG_LLM_MODEL=gemini-2.0-flash "
                "uv run uvicorn sentinelrag.api.app:app --host 0.0.0.0 --port 8000 "
                "> /tmp/sentinelrag-api.log 2>&1 </dev/null & disown; echo started'"
            ),
            "sleep 20",
            f"{path_export} && cd {remote} && uv run pytest -q",
            f"{path_export} && cd {remote} && uv run sentinelrag-gate run --refresh",
            (
                f"{path_export} && cd {remote} && "
                "SENTINELRAG_EMBEDDING_MODEL=BAAI/bge-small-en-v1.5 "
                "uv run python benchmarks/run_phase1_real.py"
            ),
            f"{path_export} && cd {remote} && uv run python scripts/demo_60s.py",
            "curl -sf http://127.0.0.1:8000/health",
        ]
        for cmd in steps:
            print(f"\n>>> {cmd[:100]}")
            soft = cmd.startswith(soft_prefixes) or any(s in cmd for s in soft_contains)
            run_ssh(client, cmd, timeout=3600, allow_fail=soft)

        # Pull real benchmark results back
        for name in ("phase1_retrieval_real.json",):
            remote_f = f"{remote}/benchmarks/{name}"
            local_f = repo / "benchmarks" / name
            try:
                sftp.get(remote_f, str(local_f))
                print(f"Fetched {name}")
            except OSError as exc:
                print(f"Skip fetch {name}: {exc}")

        print("\nAzure real-model track complete.")
    finally:
        client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
