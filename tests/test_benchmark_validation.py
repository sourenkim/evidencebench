import json
from pathlib import Path

import pytest

from evidencebench.benchmark import validate_benchmark
from evidencebench.errors import InputError


def test_benchmark_validation_rejects_missing_sources_and_bad_status(tmp_path: Path) -> None:
    (tmp_path / "documents").mkdir()
    (tmp_path / "cases").mkdir()
    (tmp_path / "documents" / "source.md").write_text("source", encoding="utf-8")
    case = {
        "id": "bad",
        "question": "q",
        "answer": "a",
        "sources": ["missing.md"],
        "expected_statuses": ["NOT_A_STATUS"],
    }
    (tmp_path / "cases" / "bad.json").write_text(json.dumps(case), encoding="utf-8")
    with pytest.raises(InputError, match="invalid expected_statuses"):
        validate_benchmark(tmp_path)
    case["expected_statuses"] = ["SUPPORTED"]
    (tmp_path / "cases" / "bad.json").write_text(json.dumps(case), encoding="utf-8")
    with pytest.raises(InputError, match="missing sources"):
        validate_benchmark(tmp_path)
