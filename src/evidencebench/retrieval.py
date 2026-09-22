"""Evidence retrieval strategies."""

from __future__ import annotations

from typing import Protocol

from .models import Chunk, Evidence
from .text import overlap_score


class EvidenceRetriever(Protocol):
    name: str

    def retrieve(self, query: str) -> tuple[Evidence, ...]: ...


class LexicalRetriever:
    """Stable token-overlap retrieval with no network calls or learned weights."""

    name = "lexical-overlap-v0.1"

    def __init__(self, chunks: tuple[Chunk, ...], *, top_k: int = 3, min_score: float = 0.15):
        if top_k < 1:
            raise ValueError("top_k must be positive")
        if not 0.0 <= min_score <= 1.0:
            raise ValueError("min_score must be between 0 and 1")
        self._chunks = chunks
        self._top_k = top_k
        self._min_score = min_score

    def retrieve(self, query: str) -> tuple[Evidence, ...]:
        ranked: list[tuple[float, Chunk]] = []
        for chunk in self._chunks:
            score = overlap_score(query, chunk.text)
            if score >= self._min_score:
                ranked.append((score, chunk))
        ranked.sort(key=lambda item: (-item[0], item[1].identifier))
        return tuple(
            Evidence(
                document_id=chunk.document_id,
                source_type=chunk.source_type,
                chunk_id=chunk.identifier,
                text=chunk.text,
                relevance_score=score,
                location=chunk.location,
            )
            for score, chunk in ranked[: self._top_k]
        )
