import pytest

from evidencebench.chunking import chunk_documents
from evidencebench.evaluation import evaluate_answer
from evidencebench.metrics import calculate_metrics, check_thresholds
from evidencebench.models import (
    Claim,
    ClaimEvaluation,
    ClaimStatus,
    Document,
    DocumentPage,
    Thresholds,
)


def source(text: str) -> tuple:
    doc = Document("source.md", "markdown", text, "source.md", (DocumentPage(text),))
    return chunk_documents((doc,))


def test_supported_partial_unsupported_and_insufficient_statuses() -> None:
    chunks = source("""# Topic

Alpha uses a red flag.

Beta uses a blue flag.
""")
    result = evaluate_answer(
        "What does the source say?",
        "Alpha uses a red flag.\nBeta uses a blue flag and lasts forever.\n"
        "Topic is made of glass.\nThe moon is made of cheese.",
        chunks,
    )
    assert [item.status for item in result.claims] == [
        ClaimStatus.SUPPORTED,
        ClaimStatus.PARTIALLY_SUPPORTED,
        ClaimStatus.UNSUPPORTED,
        ClaimStatus.INSUFFICIENT_EVIDENCE,
    ]
    assert result.metrics.total_claims == 4
    assert result.status.value == "REVIEW_REQUIRED"


def test_empty_answer_has_zero_rates_and_review_status() -> None:
    result = evaluate_answer("question", "", source("some evidence"))
    assert result.metrics.total_claims == 0
    assert result.metrics.evidence_coverage == 0.0
    assert result.status.value == "REVIEW_REQUIRED"


def test_metrics_formulas_and_duplicate_evidence_are_counted_per_claim() -> None:
    claim = Claim("c1", "claim", 1)
    evidence = object()
    items = (
        ClaimEvaluation(claim, ClaimStatus.SUPPORTED, 1, "ok", (evidence, evidence)),  # type: ignore[arg-type]
        ClaimEvaluation(
            Claim("c2", "claim", 2), ClaimStatus.PARTIALLY_SUPPORTED, 0.5, "partial", ()
        ),
        ClaimEvaluation(Claim("c3", "claim", 3), ClaimStatus.UNSUPPORTED, 0, "no", ()),
        ClaimEvaluation(Claim("c4", "claim", 4), ClaimStatus.INSUFFICIENT_EVIDENCE, 0, "none", ()),
    )
    metrics = calculate_metrics(items)
    assert metrics.evidence_coverage == 0.25
    assert metrics.unsupported_claim_rate == 0.25
    assert metrics.partial_support_rate == 0.25
    assert metrics.citation_coverage == 0.25
    assert metrics.evidence_retrieval_rate == 0.25


def test_thresholds_report_violations() -> None:
    result = evaluate_answer("q", "Alpha uses a red flag.", source("Alpha uses a red flag."))
    assert not check_thresholds(result.metrics, Thresholds(minimum_evidence_coverage=1.0))
    violations = check_thresholds(result.metrics, Thresholds(maximum_unsupported_rate=0.0))
    assert violations == ()
    with pytest.raises(Exception, match="between 0 and 1"):
        check_thresholds(result.metrics, Thresholds(minimum_evidence_coverage=1.1))
