"""Transparent metric calculations and CI threshold checks."""

from __future__ import annotations

from collections.abc import Iterable

from .errors import InputError
from .models import ClaimEvaluation, ClaimStatus, Metrics, Thresholds, ThresholdViolation


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def calculate_metrics(evaluations: Iterable[ClaimEvaluation]) -> Metrics:
    items = tuple(evaluations)
    total = len(items)
    supported = sum(item.status is ClaimStatus.SUPPORTED for item in items)
    partial = sum(item.status is ClaimStatus.PARTIALLY_SUPPORTED for item in items)
    unsupported = sum(item.status is ClaimStatus.UNSUPPORTED for item in items)
    insufficient = sum(item.status is ClaimStatus.INSUFFICIENT_EVIDENCE for item in items)
    cited = sum(bool(item.evidence) for item in items)
    return Metrics(
        total_claims=total,
        supported=supported,
        partially_supported=partial,
        unsupported=unsupported,
        insufficient_evidence=insufficient,
        # Evidence coverage is deliberately strict: only fully supported claims count.
        evidence_coverage=_rate(supported, total),
        unsupported_claim_rate=_rate(unsupported, total),
        partial_support_rate=_rate(partial, total),
        citation_coverage=_rate(cited, total),
        evidence_retrieval_rate=_rate(cited, total),
    )


def validate_thresholds(thresholds: Thresholds) -> None:
    for name, value in (
        ("minimum_evidence_coverage", thresholds.minimum_evidence_coverage),
        ("maximum_unsupported_rate", thresholds.maximum_unsupported_rate),
        ("maximum_partial_rate", thresholds.maximum_partial_rate),
    ):
        if value is not None and not 0.0 <= value <= 1.0:
            raise InputError(f"{name} must be between 0 and 1")


def check_thresholds(metrics: Metrics, thresholds: Thresholds) -> tuple[ThresholdViolation, ...]:
    validate_thresholds(thresholds)
    violations: list[ThresholdViolation] = []
    if (
        thresholds.minimum_evidence_coverage is not None
        and metrics.evidence_coverage < thresholds.minimum_evidence_coverage
    ):
        violations.append(
            ThresholdViolation(
                "evidence_coverage",
                metrics.evidence_coverage,
                ">=",
                thresholds.minimum_evidence_coverage,
            )
        )
    if (
        thresholds.maximum_unsupported_rate is not None
        and metrics.unsupported_claim_rate > thresholds.maximum_unsupported_rate
    ):
        violations.append(
            ThresholdViolation(
                "unsupported_claim_rate",
                metrics.unsupported_claim_rate,
                "<=",
                thresholds.maximum_unsupported_rate,
            )
        )
    if (
        thresholds.maximum_partial_rate is not None
        and metrics.partial_support_rate > thresholds.maximum_partial_rate
    ):
        violations.append(
            ThresholdViolation(
                "partial_support_rate",
                metrics.partial_support_rate,
                "<=",
                thresholds.maximum_partial_rate,
            )
        )
    return tuple(violations)
