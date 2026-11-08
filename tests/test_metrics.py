"""Eval metrics tests."""

from __future__ import annotations

from sentinelrag.eval.metrics import mrr, recall_at_k


def test_recall_at_k() -> None:
    rel = {"c1", "c2"}
    assert recall_at_k(["c1", "x", "c2"], rel, k=3) == 1.0
    assert recall_at_k(["x", "y"], rel, k=2) == 0.0


def test_mrr_first_hit() -> None:
    assert mrr(["x", "target", "z"], {"target"}) == 0.5
    assert mrr(["x", "y"], {"target"}) == 0.0
