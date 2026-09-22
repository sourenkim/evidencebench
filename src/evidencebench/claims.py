"""Claim extraction interfaces and a deterministic baseline implementation."""

from __future__ import annotations

import re
from typing import Protocol

from .models import Claim


class ClaimExtractor(Protocol):
    name: str

    def extract(self, answer: str) -> tuple[Claim, ...]: ...


_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])")
_BULLET_PREFIX = re.compile(r"^\s*(?:[-*•]+|\d+[.)])\s+")


def _clean_segment(segment: str) -> str:
    segment = _BULLET_PREFIX.sub("", segment.strip())
    segment = re.sub(r"^#+\s+", "", segment)
    segment = re.sub(r"\s+", " ", segment).strip()
    return segment.strip(" \t\n")


class DeterministicClaimExtractor:
    """Segment bullets, lines, and sentence boundaries without an LLM.

    This is intentionally conservative: it does not pretend that syntax alone
    can reliably identify every atomic proposition. The metadata records the
    baseline so a future model-backed extractor can be compared with it.
    """

    name = "deterministic-segmenter-v0.1"

    def extract(self, answer: str) -> tuple[Claim, ...]:
        normalized = answer.replace("\r\n", "\n").replace("\r", "\n").strip()
        if not normalized:
            return ()
        segments: list[str] = []
        for line in normalized.splitlines():
            line = line.strip()
            if not line:
                continue
            cleaned = _clean_segment(line)
            if not cleaned:
                continue
            segments.extend(_clean_segment(part) for part in _SENTENCE_BOUNDARY.split(cleaned))
        if not segments:
            segments = [_clean_segment(part) for part in _SENTENCE_BOUNDARY.split(normalized)]
        claims = [text for text in segments if text]
        return tuple(
            Claim(
                identifier=f"claim-{index}",
                text=text,
                ordinal=index,
                metadata={"extractor": self.name},
            )
            for index, text in enumerate(claims, start=1)
        )
