# Contributing

Thanks for helping improve EvidenceBench. Start with the project specification, architecture notes, and [docs/contributing.md](docs/contributing.md).

Before opening a pull request:

```bash
python -m pip install -e '.[dev]'
pytest
ruff check .
mypy src
python -m evidencebench validate benchmark
python -m evidencebench benchmark benchmark --format json > /tmp/evidencebench-benchmark.json
```

Keep the default path offline and deterministic. Include tests for behavior changes, do not add copied or restricted benchmark material, and update documentation when a metric or status changes.
