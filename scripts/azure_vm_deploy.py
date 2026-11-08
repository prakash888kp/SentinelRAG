#!/usr/bin/env python3
"""One-shot sync + bootstrap on Azure VM (reads AZURE_VM_* from .env)."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

try:
    import paramiko
except ImportError:
    print("Install paramiko: uv pip install paramiko", file=sys.stderr)
    raise SystemExit(1) from None


def load_env(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        out[key.strip()] = value.strip()
    return out


def run_ssh(client: paramiko.SSHClient, command: str, *, timeout: int = 1200) -> None:
    stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out:
        print(out, end="")
    if err:
        print(err, end="", file=sys.stderr)
    if exit_status != 0:
        raise RuntimeError(f"Command failed ({exit_status}): {command}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--env-file", type=Path, default=None)
    args = parser.parse_args()
    env_path = args.env_file or args.repo / ".env"
    if not env_path.is_file():
        print(f"Missing {env_path}", file=sys.stderr)
        return 1

    env = load_env(env_path)
    host = env.get("AZURE_VM_HOST", "")
    user = env.get("AZURE_VM_USER", "")
    password = env.get("AZURE_VM_PASSWORD", "")
    if not host or not user or not password:
        print("Set AZURE_VM_HOST, AZURE_VM_USER, AZURE_VM_PASSWORD in .env", file=sys.stderr)
        return 1

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=user, password=password, timeout=60)

    try:
        transport = client.get_transport()
        if transport is None:
            raise RuntimeError("No SSH transport")
        sftp = paramiko.SFTPClient.from_transport(transport)
        if sftp is None:
            raise RuntimeError("No SFTP")

        bootstrap = args.repo / "docs" / "azure" / "vm-bootstrap.sh"
        bootstrap_lf = bootstrap.read_bytes().replace(b"\r\n", b"\n")
        with sftp.open("/home/" + user + "/vm-bootstrap.sh", "wb") as remote_boot:
            remote_boot.write(bootstrap_lf)
        run_ssh(client, "chmod +x ~/vm-bootstrap.sh && bash ~/vm-bootstrap.sh", timeout=1200)

        remote_base = f"/home/{user}/sentinelrag"
        run_ssh(client, f"mkdir -p {remote_base}")

        skip = {".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache"}
        for path in args.repo.rglob("*"):
            if path.is_dir():
                continue
            rel = path.relative_to(args.repo)
            if any(part in skip for part in rel.parts):
                continue
            if rel.name == ".env" or rel.suffix == ".pyc":
                continue
            remote_path = remote_base + "/" + rel.as_posix()
            remote_dir = os.path.dirname(remote_path)
            run_ssh(client, f"mkdir -p {remote_dir}")
            sftp.put(str(path), remote_path)

        env_remote = remote_base + "/.env"
        sftp.put(str(env_path), env_remote)

        run_ssh(
            client,
            f"cd {remote_base} && sudo docker compose up -d --build",
            timeout=1800,
        )
        run_ssh(client, "curl -sf http://127.0.0.1:8000/health || true")
    finally:
        client.close()

    print("Deploy finished. SSH tunnel: ssh -L 8000:127.0.0.1:8000", user + "@" + host)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
