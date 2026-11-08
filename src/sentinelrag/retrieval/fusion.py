"""Hybrid score fusion."""

from __future__ import annotations


def min_max_normalize(scores: dict[str, float]) -> dict[str, float]:
    if not scores:
        return {}
    lo = min(scores.values())
    hi = max(scores.values())
    if hi <= lo:
        return dict.fromkeys(scores, 1.0)
    return {k: (v - lo) / (hi - lo) for k, v in scores.items()}


def fuse_hybrid(
    dense: dict[str, float],
    sparse: dict[str, float],
    *,
    alpha: float,
) -> list[tuple[str, float]]:
    """Weighted interpolation after per-list min-max normalization."""
    if not 0.0 <= alpha <= 1.0:
        msg = "alpha must be in [0, 1]"
        raise ValueError(msg)
    dn = min_max_normalize(dense)
    sn = min_max_normalize(sparse)
    ids = set(dn) | set(sn)
    fused = {cid: alpha * dn.get(cid, 0.0) + (1.0 - alpha) * sn.get(cid, 0.0) for cid in ids}
    return sorted(fused.items(), key=lambda x: -x[1])
