#!/usr/bin/env python3
"""Quick: sync Gemini fix, bounce API, run demo (no full tree sync)."""

from __future__ import annotations

import sys
import time
from pathlib import Path

import paramiko

sys.path.insert(0, str(Path(__file__).resolve().parent))
from azure_vm_deploy import load_env  # noqa: E402


def _exec(client: paramiko.SSHClient, cmd: str, *, timeout: int = 120) -> tuple[int, str, str]:
    _stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    return code, stdout.read().decode(), stderr.read().decode()


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    env = load_env(repo / ".env")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("connecting…")
    client.connect(
        env["AZURE_VM_HOST"],
        username=env["AZURE_VM_USER"],
        password=env["AZURE_VM_PASSWORD"],
        timeout=30,
        banner_timeout=30,
        auth_timeout=30,
    )
    remote = f"/home/{env['AZURE_VM_USER']}/sentinelrag"
    transport = client.get_transport()
    assert transport is not None
    sftp = paramiko.SFTPClient.from_transport(transport)
    assert sftp is not None
    print("uploading…")
    for rel in (
        "src/sentinelrag/generation/llm.py",
        "scripts/demo_60s.py",
        ".env",
    ):
        sftp.put(str(repo / rel), f"{remote}/{rel}")
        print(" ", rel)

    print("restart api…")
    _exec(client, "pkill -f 'uvicorn sentinelrag.api.app' || true", timeout=20)
    time.sleep(2)
    start = (
        f"cd {remote} && nohup env PATH=$HOME/.local/bin:$PATH "
        "SENTINELRAG_VECTOR_STORE_BACKEND=qdrant "
        "SENTINELRAG_QDRANT_URL=http://127.0.0.1:6333 "
        "SENTINELRAG_EMBEDDING_MODEL=BAAI/bge-small-en-v1.5 "
        "SENTINELRAG_RERANKER_MODEL=mock-reranker "
        "SENTINELRAG_LLM_PROVIDER=gemini "
        "SENTINELRAG_LLM_MODEL=gemini-2.5-flash "
        "$HOME/.local/bin/uv run uvicorn sentinelrag.api.app:app "
        "--host 0.0.0.0 --port 8000 "
        "> /tmp/sentinelrag-api.log 2>&1 </dev/null &"
    )
    # Fire-and-forget: do not wait forever for background job
    transport = client.get_transport()
    assert transport is not None
    chan = transport.open_session()
    chan.exec_command(start)
    time.sleep(3)
    chan.close()

    print("wait for health…")
    for _ in range(30):
        code, out, _err = _exec(client, "curl -sf http://127.0.0.1:8000/health || true", timeout=15)
        if '"status":"ok"' in out:
            print(out.strip())
            break
        time.sleep(2)
    else:
        _c, log, _e = _exec(client, "tail -50 /tmp/sentinelrag-api.log", timeout=20)
        print(log)
        return 1

    print("demo…")
    code, out, err = _exec(
        client,
        f"export PATH=$HOME/.local/bin:$PATH && cd {remote} && uv run python scripts/demo_60s.py",
        timeout=300,
    )
    print(out)
    if err:
        print(err, file=sys.stderr)
    if code != 0:
        _c, log, _e = _exec(client, "tail -60 /tmp/sentinelrag-api.log", timeout=20)
        print(log)
        return code
    print("OK")
    client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
