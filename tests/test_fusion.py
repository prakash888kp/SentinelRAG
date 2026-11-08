"""Hybrid fusion unit tests."""

from __future__ import annotations

import pytest

from sentinelrag.retrieval.fusion import fuse_hybrid, min_max_normalize


def test_min_max_normalize_range() -> None:
    scores = {"a": 1.0, "b": 3.0, "c": 2.0}
    norm = min_max_normalize(scores)
    assert norm["a"] == 0.0
    assert norm["b"] == 1.0
    assert norm["c"] == 0.5


def test_fuse_hybrid_alpha_weight() -> None:
    dense = {"x": 10.0, "y": 0.0}
    sparse = {"x": 0.0, "y": 10.0}
    fused = dict(fuse_hybrid(dense, sparse, alpha=1.0))
    assert fused["x"] >= fused["y"]
    fused_mix = dict(fuse_hybrid(dense, sparse, alpha=0.5))
    assert "x" in fused_mix and "y" in fused_mix


def test_fuse_hybrid_rejects_bad_alpha() -> None:
    with pytest.raises(ValueError):
        fuse_hybrid({"a": 1.0}, {"b": 1.0}, alpha=1.5)
