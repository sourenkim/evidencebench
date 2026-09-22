"""Public data structures used throughout EvidenceBench.

These classes intentionally contain no provider-specific fields. They are the
stable boundary between ingestion, retrieval, evaluation, and reporting.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ClaimStatus(StrEnum):
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class EvaluationStatus(StrEnum):
    PASS = "PASS"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


@dataclass(frozen=True, slots=True)
class SourceLocation:
    """A best-effort location; absent fields mean the loader did not know them."""

    page: int | None = None
    line_start: int | None = None
    line_end: int | None = None
    section: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "page": self.page,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "section": self.section,
        }


@dataclass(frozen=True, slots=True)
class DocumentPage:
    text: str
    page_number: int | None = None


@dataclass(frozen=True, slots=True)
class Document:
    identifier: str
    source_type: str
    text: str
    path: str
    pages: tuple[DocumentPage, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Chunk:
    identifier: str
    document_id: str
    text: str
    location: SourceLocation
    source_type: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.identifier,
            "document_id": self.document_id,
            "source_type": self.source_type,
            "text": self.text,
            "location": self.location.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class Claim:
    identifier: str
    text: str
    ordinal: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim_id": self.identifier,
            "text": self.text,
            "ordinal": self.ordinal,
            "metadata": self.metadata,
        }


@dataclass(frozen=True, slots=True)
class Evidence:
    document_id: str
    source_type: str
    chunk_id: str
    text: str
    relevance_score: float
    location: SourceLocation

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "source_type": self.source_type,
            "chunk_id": self.chunk_id,
            "text": self.text,
            "relevance_score": round(self.relevance_score, 6),
            "location": self.location.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class ClaimEvaluation:
    claim: Claim
    status: ClaimStatus
    confidence: float
    rationale: str
    evidence: tuple[Evidence, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim": self.claim.to_dict(),
            "status": self.status.value,
            "confidence": round(self.confidence, 6),
            "rationale": self.rationale,
            "evidence": [item.to_dict() for item in self.evidence],
            "metadata": self.metadata,
        }


@dataclass(frozen=True, slots=True)
class Metrics:
    total_claims: int
    supported: int
    partially_supported: int
    unsupported: int
    insufficient_evidence: int
    evidence_coverage: float
    unsupported_claim_rate: float
    partial_support_rate: float
    citation_coverage: float
    evidence_retrieval_rate: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_claims": self.total_claims,
            "supported": self.supported,
            "partially_supported": self.partially_supported,
            "unsupported": self.unsupported,
            "insufficient_evidence": self.insufficient_evidence,
            "evidence_coverage": self.evidence_coverage,
            "unsupported_claim_rate": self.unsupported_claim_rate,
            "partial_support_rate": self.partial_support_rate,
            "citation_coverage": self.citation_coverage,
            "evidence_retrieval_rate": self.evidence_retrieval_rate,
        }


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    question: str
    answer: str
    claims: tuple[ClaimEvaluation, ...]
    metrics: Metrics
    status: EvaluationStatus
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "0.1",
            "question": self.question,
            "answer": self.answer,
            "status": self.status.value,
            "metrics": self.metrics.to_dict(),
            "claims": [item.to_dict() for item in self.claims],
            "metadata": self.metadata,
        }


@dataclass(frozen=True, slots=True)
class Thresholds:
    minimum_evidence_coverage: float | None = None
    maximum_unsupported_rate: float | None = None
    maximum_partial_rate: float | None = None


@dataclass(frozen=True, slots=True)
class ThresholdViolation:
    metric: str
    actual: float
    operator: str
    threshold: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric": self.metric,
            "actual": self.actual,
            "operator": self.operator,
            "threshold": self.threshold,
        }
