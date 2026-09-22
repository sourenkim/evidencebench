"""Small, dependency-free text utilities used by retrieval and evaluation."""

from __future__ import annotations

import re
from collections import Counter

_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "because",
    "by",
    "can",
    "for",
    "from",
    "has",
    "have",
    "in",
    "is",
    "it",
    "may",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "was",
    "were",
    "will",
    "with",
    "you",
    "your",
    "document",
    "source",
    "states",
    "state",
    "says",
    "say",
    "according",
    "reports",
    "report",
}
_TOKEN_RE = re.compile(r"[\w]+(?:['-][\w]+)*", flags=re.UNICODE)
_NEGATION = {"no", "not", "never", "without", "cannot", "isn't", "aren't", "doesn't", "don't"}


def tokens(text: str, *, remove_stopwords: bool = True) -> list[str]:
    values = [value.casefold() for value in _TOKEN_RE.findall(text)]
    if remove_stopwords:
        return [value for value in values if value not in _STOPWORDS]
    return values


def token_set(text: str) -> set[str]:
    return set(tokens(text))


def token_counter(text: str) -> Counter[str]:
    return Counter(tokens(text))


def overlap_score(query: str, candidate: str) -> float:
    query_tokens = token_set(query)
    if not query_tokens:
        return 0.0
    return len(query_tokens & token_set(candidate)) / len(query_tokens)


def negation_tokens(text: str) -> set[str]:
    return set(tokens(text, remove_stopwords=False)) & _NEGATION


def has_negation_mismatch(claim: str, evidence: str) -> bool:
    """Detect only a narrow, explicit polarity mismatch.

    This is not a contradiction solver. It avoids labeling a claim unsupported
    merely because a document contains a negation elsewhere.
    """
    claim_words = tokens(claim, remove_stopwords=False)
    evidence_words = tokens(evidence, remove_stopwords=False)
    claim_negated = bool(set(claim_words) & _NEGATION)
    evidence_negated = bool(set(evidence_words) & _NEGATION)
    if claim_negated == evidence_negated:
        return False
    claim_content = set(tokens(claim))
    evidence_content = set(tokens(evidence))
    return len(claim_content & evidence_content) >= max(1, min(3, len(claim_content) // 2))
