#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import paramiko

from azure_vm_deploy import load_env


def main() -> None:
    env = load_env(Path(__file__).resolve().parents[1] / ".env")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        env["AZURE_VM_HOST"],
        username=env["AZURE_VM_USER"],
        password=env["AZURE_VM_PASSWORD"],
        timeout=30,
    )
    cmds = [
        "ps -ef | grep -E 'uvicorn|uv |python' | grep -v grep | head -30",
        "tail -40 /tmp/sentinelrag-api.log 2>/dev/null || echo no_api_log",
        "curl -sf http://127.0.0.1:8000/health || echo health_fail",
        "df -h / | tail -1",
        "free -h",
    ]
    for cmd in cmds:
        print("===", cmd)
        _stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print("ERR", err)
    client.close()


if __name__ == "__main__":
    main()
