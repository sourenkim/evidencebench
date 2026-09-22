# Contributing

EvidenceBench values small, reviewable changes over feature count.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
ruff check .
mypy src
```

The default test suite must not make network calls or require paid APIs. Add fixtures for edge cases and document any behavior that intentionally remains heuristic.

## Pull requests

- Explain the behavior and the reason for the change.
- Add or update tests for public behavior.
- Update docs, the changelog, and decision log when the design changes.
- Do not commit credentials, generated reports, or copyrighted fixtures.
- Run the same commands as CI before opening a pull request.

## Design expectations

Keep deterministic components separate from provider-dependent components. Preserve uncertainty rather than forcing binary truth. Do not fabricate locations, benchmark values, or provider support. Security-sensitive changes should include a threat-model note.
