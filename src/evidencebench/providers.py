"""Provider protocols for optional model-dependent integrations.

No provider SDK is imported here. Adapters can implement these protocols in a
separate package or in an application using EvidenceBench. Source text should
be passed as delimited data, never as instructions.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from .models import Claim, ClaimEvaluation, Evidence


class LLMProvider(Protocol):
    """Minimal interface for model-backed claim extraction or verification."""

    name: str

    def extract_claims(self, question: str, answer: str) -> Sequence[Claim]: ...

    def evaluate_claim(
        self,
        question: str,
        claim: Claim,
        evidence: Sequence[Evidence],
    ) -> ClaimEvaluation: ...


class EmbeddingProvider(Protocol):
    """Optional interface for semantic retrieval."""

    name: str

    def embed(self, texts: Sequence[str]) -> Sequence[Sequence[float]]: ...

    def similarity(self, query: Sequence[float], candidate: Sequence[float]) -> float: ...


@dataclass(frozen=True, slots=True)
class ProviderConfiguration:
    """Metadata recorded in reports when an external provider is used."""

    name: str
    model: str | None = None
    data_sent_remotely: bool = False
