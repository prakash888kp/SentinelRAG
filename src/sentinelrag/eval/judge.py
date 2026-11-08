"""LLM-as-judge with versioned prompts and MockJudge for CI."""

from __future__ import annotations

import hashlib
import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from sentinelrag.generation.llm import LLMProvider, Message, get_llm
from sentinelrag.settings import Settings, get_settings

_JUDGE_ROOT = Path(__file__).resolve().parent / "judges"


@dataclass(frozen=True, slots=True)
class JudgeScore:
    score: float
    reason: str
    prompt_version: str


class Judge(ABC):
    @abstractmethod
    def faithfulness(self, *, context: str, question: str, answer: str) -> JudgeScore:
        """Score how well ``answer`` is supported by ``context``."""

    @abstractmethod
    def relevance(self, *, question: str, answer: str) -> JudgeScore:
        """Score how well ``answer`` addresses ``question``."""


def load_prompt(version: str, name: str) -> str:
    path = _JUDGE_ROOT / version / f"{name}.txt"
    if not path.is_file():
        msg = f"Missing judge prompt: {path}"
        raise FileNotFoundError(msg)
    return path.read_text(encoding="utf-8")


def _parse_judge_json(raw: str) -> tuple[float, str]:
    match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    payload = json.loads(match.group(0) if match else raw)
    score = float(payload["score"])
    reason = str(payload.get("reason", ""))
    return max(0.0, min(1.0, score)), reason


class MockJudge(Judge):
    """Deterministic lexical judge for offline CI (not a human surrogate)."""

    def __init__(self, *, prompt_version: str = "v1") -> None:
        self.prompt_version = prompt_version

    def faithfulness(self, *, context: str, question: str, answer: str) -> JudgeScore:
        _ = question
        ctx_tokens = set(context.lower().split())
        ans_tokens = [t for t in answer.lower().split() if len(t) > 3]
        if not ans_tokens:
            return JudgeScore(0.0, "empty answer", self.prompt_version)
        supported = sum(1 for t in ans_tokens if t in ctx_tokens)
        score = supported / len(ans_tokens)
        # Stable tie-break from content hash for reproducibility.
        digest = hashlib.sha256(f"{context}:{answer}".encode()).hexdigest()
        jitter = (int(digest[:4], 16) % 7) / 100.0
        score = min(1.0, score * 0.85 + jitter)
        return JudgeScore(round(score, 4), "mock lexical overlap", self.prompt_version)

    def relevance(self, *, question: str, answer: str) -> JudgeScore:
        q = set(question.lower().split())
        a = set(answer.lower().split())
        overlap = len(q & a) / max(len(q), 1)
        score = min(1.0, overlap + 0.5)
        return JudgeScore(round(score, 4), "mock question overlap", self.prompt_version)


class LLMJudge(Judge):
    """Uses configured LLM provider with versioned prompts (network in prod)."""

    def __init__(
        self,
        *,
        llm: LLMProvider | None = None,
        prompt_version: str = "v1",
        settings: Settings | None = None,
    ) -> None:
        self._llm = llm or get_llm(settings or get_settings())
        self.prompt_version = prompt_version

    def faithfulness(self, *, context: str, question: str, answer: str) -> JudgeScore:
        template = load_prompt(self.prompt_version, "faithfulness")
        prompt = template.format(context=context, question=question, answer=answer)
        raw = self._llm.complete([Message(role="user", content=prompt)])
        score, reason = _parse_judge_json(raw)
        return JudgeScore(score, reason, self.prompt_version)

    def relevance(self, *, question: str, answer: str) -> JudgeScore:
        template = load_prompt(self.prompt_version, "relevance")
        prompt = template.format(question=question, answer=answer)
        raw = self._llm.complete([Message(role="user", content=prompt)])
        score, reason = _parse_judge_json(raw)
        return JudgeScore(score, reason, self.prompt_version)


def get_judge(settings: Settings | None = None) -> Judge:
    cfg = settings or get_settings()
    if cfg.llm_provider == "mock":
        return MockJudge()
    return LLMJudge(settings=cfg)
