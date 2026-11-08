#!/usr/bin/env python3
"""Push Gemini fix + restart API + run 60s demo on Azure VM."""

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
    transport = client.get_transport()
    assert transport is not None
    sftp = paramiko.SFTPClient.from_transport(transport)
    assert sftp is not None
    for rel in (
        "src/sentinelrag/generation/llm.py",
        "scripts/demo_60s.py",
        ".env",
    ):
        sftp.put(str(repo / rel), f"{remote}/{rel}")

    pe = "export PATH=$HOME/.local/bin:$PATH"
    run_ssh(client, "pkill -f 'uvicorn sentinelrag.api.app' || true", allow_fail=True)
    run_ssh(
        client,
        (
            f"bash -lc '{pe} && cd {remote} && "
            "nohup env SENTINELRAG_VECTOR_STORE_BACKEND=qdrant "
            "SENTINELRAG_QDRANT_URL=http://127.0.0.1:6333 "
            "SENTINELRAG_EMBEDDING_MODEL=BAAI/bge-small-en-v1.5 "
            "SENTINELRAG_RERANKER_MODEL=mock-reranker "
            "SENTINELRAG_LLM_PROVIDER=gemini "
            "SENTINELRAG_LLM_MODEL=gemini-2.5-flash "
            "uv run uvicorn sentinelrag.api.app:app --host 0.0.0.0 --port 8000 "
            "> /tmp/sentinelrag-api.log 2>&1 </dev/null & disown; echo started'"
        ),
    )
    run_ssh(client, "sleep 12")
    run_ssh(client, f"{pe} && cd {remote} && uv run python scripts/demo_60s.py", timeout=300)
    run_ssh(client, "curl -sf http://127.0.0.1:8000/health")
    print("Gemini demo OK")
    client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
