#!/usr/bin/env python3
"""SSH to Azure VM and run release verification (pytest + gate + health)."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import paramiko
except ImportError:
    print("Install paramiko: uv sync --extra dev", file=sys.stderr)
    raise SystemExit(1) from None

from azure_vm_deploy import load_env, run_ssh  # type: ignore[import-not-found]


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    env = load_env(repo / ".env")
    host, user, password = (
        env.get("AZURE_VM_HOST", ""),
        env.get("AZURE_VM_USER", ""),
        env.get("AZURE_VM_PASSWORD", ""),
    )
    if not host or not user or not password:
        print("Missing AZURE_VM_* in .env", file=sys.stderr)
        return 1

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {user}@{host} …")
    client.connect(hostname=host, username=user, password=password, timeout=60)
    try:
        remote = f"/home/{user}/sentinelrag"
        cmds = [
            f"cd {remote} && command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh",
            f"export PATH=$HOME/.local/bin:$PATH && cd {remote} && uv sync --extra dev",
            f"export PATH=$HOME/.local/bin:$PATH && cd {remote} && uv run pytest -q",
            f"export PATH=$HOME/.local/bin:$PATH && cd {remote} && uv run sentinelrag-gate run --refresh",
            "curl -sf http://127.0.0.1:8000/health || sudo docker compose -f "
            f"{remote}/docker-compose.yml ps",
        ]
        for cmd in cmds:
            print(f"\n>>> {cmd[:90]}…")
            run_ssh(client, cmd, timeout=1800)
        print("\nAzure VM verification passed.")
    finally:
        client.close()
    return 0


if __name__ == "__main__":
    # Allow importing sibling script without package install
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
