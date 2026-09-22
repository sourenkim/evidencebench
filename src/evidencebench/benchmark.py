"""Reproducible benchmark dataset validation and execution."""

from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path
from typing import Any

from .chunking import chunk_documents
from .errors import InputError
from .evaluation import evaluate_answer
from .ingestion import load_documents
from .models import ClaimStatus


def _read_case(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InputError(f"Invalid benchmark case {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise InputError(f"Benchmark case must be an object: {path}")
    required = {"id", "question", "answer", "sources", "expected_statuses"}
    missing = required - value.keys()
    if missing:
        raise InputError(f"Benchmark case {path} is missing: {', '.join(sorted(missing))}")
    if not all(isinstance(value.get(field), str) for field in ("id", "question", "answer")):
        raise InputError(f"Benchmark case {path} has a non-string id, question, or answer")
    statuses = value["expected_statuses"]
    allowed_statuses = {status.value for status in ClaimStatus}
    if not isinstance(statuses, list) or not all(
        isinstance(status, str) and status in allowed_statuses for status in statuses
    ):
        raise InputError(f"Benchmark case {path} has invalid expected_statuses")
    sources = value["sources"]
    if (
        not isinstance(sources, list)
        or not sources
        or not all(isinstance(source, str) for source in sources)
    ):
        raise InputError(f"Benchmark case {path} must list string sources")
    return value


def validate_benchmark(path: str | Path) -> int:
    root = Path(path)
    documents_dir = root / "documents"
    cases_dir = root / "cases"
    if not documents_dir.is_dir() or not cases_dir.is_dir():
        raise InputError("Benchmark directory must contain documents/ and cases/")
    documents = load_documents(documents_dir)
    document_ids = {document.identifier for document in documents}
    cases = sorted(cases_dir.glob("*.json"))
    if not cases:
        raise InputError("Benchmark cases/ contains no JSON cases")
    for case_path in cases:
        case = _read_case(case_path)
        unknown = set(case["sources"]) - document_ids
        if unknown:
            raise InputError(
                f"{case_path.name} references missing sources: {', '.join(sorted(unknown))}"
            )
        if len(case["expected_statuses"]) == 0:
            raise InputError(f"{case_path.name} has no expected claims")
    return len(cases)


def run_benchmark(path: str | Path) -> dict[str, Any]:
    root = Path(path)
    validate_benchmark(root)
    all_documents = load_documents(root / "documents")
    by_id = {document.identifier: document for document in all_documents}
    cases = sorted(root.joinpath("cases").glob("*.json"))
    started = time.perf_counter()
    expected_counter: Counter[str] = Counter()
    predicted_counter: Counter[str] = Counter()
    confusion: Counter[tuple[str, str]] = Counter()
    invalid_claim_counts = 0
    per_case: list[dict[str, Any]] = []
    total_claims = 0
    for case_path in cases:
        case = _read_case(case_path)
        source_documents = tuple(by_id[source] for source in case["sources"])
        chunks = chunk_documents(source_documents)
        result = evaluate_answer(case["question"], case["answer"], chunks)
        expected = [str(status) for status in case["expected_statuses"]]
        predicted = [item.status.value for item in result.claims]
        if len(expected) != len(predicted):
            invalid_claim_counts += 1
        for index in range(max(len(expected), len(predicted))):
            expected_status = expected[index] if index < len(expected) else "MISSING_EXPECTED"
            predicted_status = predicted[index] if index < len(predicted) else "MISSING_PREDICTED"
            if expected_status in ClaimStatus:
                expected_counter[expected_status] += 1
            if predicted_status in ClaimStatus:
                predicted_counter[predicted_status] += 1
            confusion[(expected_status, predicted_status)] += 1
        total_claims += len(expected)
        per_case.append(
            {
                "id": case["id"],
                "expected_claims": len(expected),
                "predicted_claims": len(predicted),
                "exact_status_match": expected == predicted,
            }
        )
    elapsed = time.perf_counter() - started
    detection: dict[str, float] = {}
    false_positive: dict[str, float] = {}
    for status in ClaimStatus:
        true_positive = confusion[(status.value, status.value)]
        actual = expected_counter[status.value]
        predicted_as_status = predicted_counter[status.value]
        negatives = total_claims - actual
        false_positives = predicted_as_status - true_positive
        detection[status.value] = true_positive / actual if actual else 0.0
        false_positive[status.value] = false_positives / negatives if negatives else 0.0
    exact_cases = sum(item["exact_status_match"] for item in per_case)
    return {
        "dataset": root.as_posix(),
        "examples": len(cases),
        "expected_claims": total_claims,
        "exact_case_match_rate": exact_cases / len(cases) if cases else 0.0,
        "status_detection_recall": detection,
        "status_false_positive_rate": false_positive,
        "invalid_claim_count_cases": invalid_claim_counts,
        "runtime_seconds": elapsed,
        "confusion": {
            f"{expected} -> {predicted}": count
            for (expected, predicted), count in sorted(confusion.items())
        },
        "cases": per_case,
    }


def render_benchmark_terminal(summary: dict[str, Any]) -> str:
    recall = summary["status_detection_recall"]
    fpr = summary["status_false_positive_rate"]
    lines = [
        "EvidenceBench Benchmark",
        "=" * 24,
        f"Examples: {summary['examples']}",
        f"Expected claims: {summary['expected_claims']}",
        f"Exact case status match: {summary['exact_case_match_rate']:.1%}",
        "",
    ]
    for status in ClaimStatus:
        lines.append(
            f"{status.value.title().replace('_', ' ')} detection: {recall[status.value]:.1%}"
        )
    lines.extend(
        [
            "",
            "False positive rates",
            *[
                f"  {status.value.title().replace('_', ' ')}: {fpr[status.value]:.1%}"
                for status in ClaimStatus
            ],
            "",
            f"Invalid claim-count cases: {summary['invalid_claim_count_cases']}",
            f"Runtime: {summary['runtime_seconds']:.3f}s",
        ]
    )
    return "\n".join(lines)
