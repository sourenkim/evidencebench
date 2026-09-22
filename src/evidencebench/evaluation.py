"""Claim/evidence evaluation and orchestration of the deterministic pipeline."""

from __future__ import annotations

from .claims import ClaimExtractor, DeterministicClaimExtractor
from .metrics import calculate_metrics
from .models import (
    Chunk,
    Claim,
    ClaimEvaluation,
    ClaimStatus,
    EvaluationResult,
    EvaluationStatus,
    Evidence,
)
from .retrieval import EvidenceRetriever, LexicalRetriever
from .text import has_negation_mismatch, overlap_score, token_set


class LexicalClaimEvaluator:
    """Conservative baseline evaluator.

    It measures content-token coverage in the best retrieved snippet. The
    thresholds are intentionally visible and are not a probability of truth.
    """

    name = "lexical-coverage-v0.1"

    def evaluate(self, claim: Claim, evidence: tuple[Evidence, ...]) -> ClaimEvaluation:
        if not evidence:
            return ClaimEvaluation(
                claim=claim,
                status=ClaimStatus.INSUFFICIENT_EVIDENCE,
                confidence=0.0,
                rationale="No candidate evidence met the retrieval threshold.",
                metadata={"evaluator": self.name, "confidence_kind": "heuristic"},
            )
        best = evidence[0]
        coverage = overlap_score(claim.text, best.text)
        claim_tokens = token_set(claim.text)
        evidence_tokens = token_set(best.text)
        contradiction = has_negation_mismatch(claim.text, best.text)
        if contradiction:
            status = ClaimStatus.UNSUPPORTED
            rationale = (
                "Retrieved evidence shares the claim's subject matter but contains an "
                "explicit polarity mismatch."
            )
        elif not claim_tokens:
            status = ClaimStatus.INSUFFICIENT_EVIDENCE
            rationale = "The claim contains no evaluable content words."
        elif coverage >= 0.8:
            status = ClaimStatus.SUPPORTED
            rationale = "The highest-ranked evidence covers the claim's content words."
        elif coverage >= 0.35:
            status = ClaimStatus.PARTIALLY_SUPPORTED
            rationale = (
                f"Retrieved evidence covers {coverage:.0%} of the claim's content words; "
                "the remaining claim content is not established by this baseline."
            )
        else:
            status = ClaimStatus.UNSUPPORTED
            rationale = (
                f"Retrieved evidence overlaps only {coverage:.0%} of the claim's content words "
                "and is not adequate support."
            )
        confidence = min(1.0, max(0.0, coverage))
        if status is ClaimStatus.INSUFFICIENT_EVIDENCE:
            confidence = 0.0
        return ClaimEvaluation(
            claim=claim,
            status=status,
            confidence=confidence,
            rationale=rationale,
            evidence=evidence,
            metadata={
                "evaluator": self.name,
                "confidence_kind": "heuristic_overlap",
                "content_word_coverage": round(coverage, 6),
                "matched_content_words": sorted(claim_tokens & evidence_tokens),
            },
        )


def evaluate_answer(
    question: str,
    answer: str,
    chunks: tuple[Chunk, ...],
    *,
    extractor: ClaimExtractor | None = None,
    retriever: EvidenceRetriever | None = None,
    evaluator: LexicalClaimEvaluator | None = None,
) -> EvaluationResult:
    """Run the complete default pipeline over pre-chunked source material."""
    selected_extractor = extractor or DeterministicClaimExtractor()
    selected_retriever = retriever or LexicalRetriever(chunks)
    selected_evaluator = evaluator or LexicalClaimEvaluator()
    claims = selected_extractor.extract(answer)
    evaluations: list[ClaimEvaluation] = []
    for claim in claims:
        evidence = selected_retriever.retrieve(claim.text)
        evaluations.append(selected_evaluator.evaluate(claim, evidence))
    result_metrics = calculate_metrics(tuple(evaluations))
    result_status = (
        EvaluationStatus.PASS
        if result_metrics.total_claims > 0
        and result_metrics.partially_supported == 0
        and result_metrics.unsupported == 0
        and result_metrics.insufficient_evidence == 0
        else EvaluationStatus.REVIEW_REQUIRED
    )
    return EvaluationResult(
        question=question,
        answer=answer,
        claims=tuple(evaluations),
        metrics=result_metrics,
        status=result_status,
        metadata={
            "claim_extractor": getattr(
                selected_extractor, "name", type(selected_extractor).__name__
            ),
            "retriever": getattr(selected_retriever, "name", type(selected_retriever).__name__),
            "evaluator": getattr(selected_evaluator, "name", type(selected_evaluator).__name__),
            "deterministic": True,
        },
    )
