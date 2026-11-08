"""Golden dataset JSONL interchange."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def export_jsonl(items: list[dict[str, Any]], path: Path) -> None:
    lines = [json.dumps(item, ensure_ascii=False) for item in items]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def from_golden_dataset(dataset_path: Path, out_path: Path) -> None:
    data = json.loads(dataset_path.read_text(encoding="utf-8"))
    items = []
    for row in data.get("items", []):
        items.append(
            {
                "id": row["id"],
                "query": row["query"],
                "expected_chunk_ids": row.get("relevant_chunk_ids", []),
                "kind": row.get("item_type", "single_hop"),
                "citations_required": True,
            }
        )
    export_jsonl(items, out_path)
