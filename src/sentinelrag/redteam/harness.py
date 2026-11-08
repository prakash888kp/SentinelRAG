"""Red-team harness: Attack Success Rate (retrieval + generation)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from sentinelrag.ingest.pipeline import IndexState, ingest_corpus_dir
from sentinelrag.ingest.schema import ChunkPayload
from sentinelrag.paths import mini_corpus_dir
from sentinelrag.redteam.attacks import (
    dual_sleeper_trigger,
    metadata_only_poison,
    single_document_poison,
)
from sentinelrag.redteam.defenses import LexicalAnomalyFilter, MetadataTrustFilter
from sentinelrag.retrieval.bm25_index import BM25Index
from sentinelrag.retrieval.fusion import fuse_hybrid
from sentinelrag.retrieval.stores import InMemoryVectorStore
from sentinelrag.settings import Settings, settings_without_dotenv


@dataclass(frozen=True, slots=True)
class AttackOutcome:
    attack: str
    retrieval_asr: float
    generation_asr: float
    poison_in_top_k: bool


def _index_with_poison(
    *,
    poison_chunks: list[ChunkPayload],
    settings: Settings,
    alpha: float,
) -> tuple[IndexState, InMemoryVectorStore]:
    cfg = settings.model_copy(update={"hybrid_alpha": alpha})
    state = IndexState()
    ingest_corpus_dir(mini_corpus_dir(), state, settings=cfg)
    assert state.store is not None and state.embedder is not None
    store = state.store
    if not isinstance(store, InMemoryVectorStore):
        store = InMemoryVectorStore()
        state.store = store
    for chunk in poison_chunks:
        state.chunks[chunk.chunk_id] = chunk
    all_chunks = list(state.chunks.values())
    vectors = [state.embedder.embed(c.text) for c in all_chunks]
    store.clear()
    store.upsert(all_chunks, vectors)
    bm25 = BM25Index()
    bm25.add_chunks(all_chunks)
    state.bm25 = bm25
    return state, store


def _retrieve_ids(
    state: IndexState,
    store: InMemoryVectorStore,
    query: str,
    *,
    alpha: float,
    top_k: int,
) -> list[str]:
    assert state.embedder is not None
    vec = state.embedder.embed(query)
    dense = {h.chunk_id: h.score for h in store.search(vec, top_k=top_k * 3)}
    sparse = state.bm25.search(query, top_k=top_k * 3)
    fused = fuse_hybrid(dense, sparse, alpha=alpha)
    return [cid for cid, _ in fused[:top_k]]


def run_redteam(*, alpha: float = 0.5) -> dict[str, Any]:
    cfg = settings_without_dotenv(
        embedding_model="mock-embedder",
        hybrid_alpha=alpha,
        vector_store_backend="memory",
    )
    attacks = [
        (single_document_poison(trigger_query="What is SentinelRAG?"), "What is SentinelRAG?"),
        (dual_sleeper_trigger(), "RELEASE_KEYWORD status"),
        (metadata_only_poison(), "Trusted System Overview"),
    ]
    outcomes: list[AttackOutcome] = []
    poison_ids = {"poison-single::0", "poison-sleeper::0", "poison-trigger::0", "poison-meta::0"}

    for sample, query in attacks:
        state, store = _index_with_poison(poison_chunks=sample.chunks, settings=cfg, alpha=alpha)
        ids = _retrieve_ids(state, store, query, alpha=alpha, top_k=cfg.retrieval_top_k)
        poison_hit = any(cid in poison_ids for cid in ids)
        gen_asr = 1.0 if poison_hit else 0.0
        outcomes.append(
            AttackOutcome(
                attack=sample.attack,
                retrieval_asr=1.0 if poison_hit else 0.0,
                generation_asr=gen_asr,
                poison_in_top_k=poison_hit,
            )
        )

    defended = _run_defense_probe(cfg)
    return {
        "hybrid_alpha": alpha,
        "attacks": [asdict(o) for o in outcomes],
        "mean_retrieval_asr": sum(o.retrieval_asr for o in outcomes) / len(outcomes),
        "mean_generation_asr": sum(o.generation_asr for o in outcomes) / len(outcomes),
        "defense_probe_blocked_fraction": defended,
    }


def _run_defense_probe(settings: Settings) -> float:
    """Fraction of poison docs blocked by default defenses."""
    meta_filter = MetadataTrustFilter()
    lex_filter = LexicalAnomalyFilter()
    samples = [
        metadata_only_poison().chunks[0],
        single_document_poison(trigger_query="What is SentinelRAG?").chunks[0],
    ]
    blocked = 0
    for chunk in samples:
        ok = meta_filter.accept(chunk.metadata, chunk.text) and lex_filter.accept(
            chunk.metadata, chunk.text
        )
        if not ok:
            blocked += 1
    return blocked / len(samples)
