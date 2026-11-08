#!/usr/bin/env python3
"""Resume Azure real-model checks assuming API already running."""

from __future__ import annotations

import sys
from pathlib import Path

import paramiko

sys.path.insert(0, str(Path(__file__).resolve().parent))
from azure_vm_deploy import load_env, run_ssh  # noqa: E402


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    env = load_env(repo / ".env")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        env["AZURE_VM_HOST"],
        username=env["AZURE_VM_USER"],
        password=env["AZURE_VM_PASSWORD"],
        timeout=60,
    )
    remote = f"/home/{env['AZURE_VM_USER']}/sentinelrag"
    pe = "export PATH=$HOME/.local/bin:$PATH"
    # Upload demo + real bench scripts
    transport = client.get_transport()
    assert transport is not None
    sftp = paramiko.SFTPClient.from_transport(transport)
    assert sftp is not None
    for rel in ("scripts/demo_60s.py", "benchmarks/run_phase1_real.py"):
        sftp.put(str(repo / rel), f"{remote}/{rel}")

    cmds = [
        f"{pe} && cd {remote} && uv run pytest -q",
        f"{pe} && cd {remote} && uv run sentinelrag-gate run --refresh",
        (
            f"{pe} && cd {remote} && "
            "SENTINELRAG_EMBEDDING_MODEL=BAAI/bge-small-en-v1.5 "
            "uv run python benchmarks/run_phase1_real.py"
        ),
        f"{pe} && cd {remote} && uv run python scripts/demo_60s.py",
        "curl -sf http://127.0.0.1:8000/health",
    ]
    try:
        for cmd in cmds:
            print(f"\n>>> {cmd[:110]}")
            run_ssh(client, cmd, timeout=3600)
        local = repo / "benchmarks" / "phase1_retrieval_real.json"
        sftp.get(f"{remote}/benchmarks/phase1_retrieval_real.json", str(local))
        print(f"Fetched {local}")
        print("\nAzure real-model resume complete.")
    finally:
        client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
