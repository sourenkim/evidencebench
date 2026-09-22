from pathlib import Path

from evidencebench.benchmark import run_benchmark, validate_benchmark


def test_repository_benchmark_is_valid_and_reproducible_shape() -> None:
    root = Path(__file__).parents[1] / "benchmark"
    assert validate_benchmark(root) == 100
    summary = run_benchmark(root)
    assert summary["examples"] == 100
    assert summary["expected_claims"] == 480
    assert summary["invalid_claim_count_cases"] == 0
    assert 0.0 <= summary["exact_case_match_rate"] <= 1.0
