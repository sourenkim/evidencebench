# EvidenceBench

> An open-source testing framework for measuring whether AI-generated answers are actually supported by their source documents.
>
> Think pytest for AI grounding.

EvidenceBench is a local-first Python CLI that decomposes an answer into claims, retrieves candidate source snippets, classifies each claim, and reports transparent metrics. The default implementation is deterministic and needs no API key.

## Installation

Python 3.11 or newer is required.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
# Optional PDF extraction:
python -m pip install -e '.[pdf]'
```

For development:

```bash
python -m pip install -e '.[dev]'
```

## Quick start

```bash
evidencebench evaluate \
  --sources ./examples/docs \
  --question ./examples/question.txt \
  --answer ./examples/answer.txt
```

The command reads files locally and prints claim-level details:

```text
EvidenceBench Evaluation
==========================
Status: REVIEW_REQUIRED
Claims: 3
Supported: 2
Partially supported: 0
Unsupported: 1
Insufficient evidence: 0

Evidence coverage (fully supported): 66.7%
Unsupported claim rate: 33.3%
Citation coverage: 100.0%
Evidence retrieval rate: 100.0%
```

The exact output depends on the input. Produce machine-readable or standalone reports with:

```bash
evidencebench evaluate ... --format json --output reports/
evidencebench evaluate ... --format html --output reports/
```

HTML is static, self-contained, and does not run JavaScript. All source text is escaped before it is inserted into the report.

## What the MVP does

- Reads TXT and Markdown files locally; PDF extraction is available with the optional `pypdf` extra.
- Segments bullets and sentences into independently evaluated claims.
- Retrieves evidence using deterministic normalized-token overlap.
- Classifies claims as `SUPPORTED`, `PARTIALLY_SUPPORTED`, `UNSUPPORTED`, or `INSUFFICIENT_EVIDENCE`.
- Preserves document, chunk, line, section, and PDF page metadata when it is available.
- Calculates evidence coverage, unsupported claim rate, partial support rate, citation coverage, and evidence retrieval rate.
- Emits terminal, JSON, and no-JavaScript HTML reports.
- Enforces thresholds for CI without calling external APIs.

This baseline is intentionally not a semantic truth oracle. It is a reproducible reference implementation and a clean boundary for stronger retrieval or model-backed adapters.

## Regression testing in CI

```bash
evidencebench assert \
  --sources ./examples/docs \
  --question ./examples/question.txt \
  --answer ./examples/answer.txt \
  --minimum-evidence-coverage 0.90 \
  --maximum-unsupported-rate 0.05 \
  --maximum-partial-rate 0.10
```

A failed threshold returns a non-zero exit code. The `assert` command does not hide the underlying claim report.

## Benchmark

The repository includes 20 original Markdown documents, 100 cases, and 480 labeled claims:

```bash
evidencebench validate benchmark
evidencebench benchmark benchmark
evidencebench benchmark benchmark --format json --output reports/benchmark.json
```

Benchmark metrics are computed when the command runs. This README does not claim a fixed score because results are implementation output, not a promise. See [`docs/benchmark.md`](docs/benchmark.md) for the dataset format and interpretation.

## Architecture

```text
sources + question + answer
            |
  ingestion -> normalization -> chunking
            |
  claim extraction -> retrieval -> claim evaluation
            |
       metrics -> terminal / JSON / HTML report
```

The pipeline is split into deterministic components with small interfaces. Provider protocols in `evidencebench.providers` allow future LLM and embedding adapters without importing a vendor SDK or sending documents anywhere by default. Read [`docs/architecture.md`](docs/architecture.md) and [`docs/concepts.md`](docs/concepts.md) before extending it.

## Metrics and interpretation

Evidence coverage is the percentage of claims classified fully `SUPPORTED`; partial claims are reported separately and do not silently count as fully covered. Citation coverage means that at least one retrieved evidence item is attached to a claim. Evidence retrieval rate means that the retriever returned at least one candidate above its threshold. These are not measures of model confidence or universal factual truth. Definitions, formulas, and limitations are in [`docs/metrics.md`](docs/metrics.md).

## Security and privacy

Files are treated as untrusted data. Source text is never interpreted as software instructions, and static report generation escapes HTML. The default pipeline is local and collects no telemetry. If an application adds a remote provider, that adapter is responsible for explicit consent, secret handling, and documenting which question, answer, and source text leave the machine. See [`docs/security.md`](docs/security.md).

## Examples

- `examples/docs/` and the small text inputs are a runnable TXT/Markdown example.
- `examples/rag_workflow.py` demonstrates a retrieval-like workflow using the library API.
- `examples/ci_assert.sh` shows a CI-friendly assertion.
- `examples/unsupported_claim/` demonstrates an unsupported claim and report output.

## Limitations and roadmap

The deterministic baseline misses paraphrases, complex negation, cross-sentence entailment, tables, and domain-specific reasoning. PDF text extraction quality depends on `pypdf`; scanned PDFs need OCR, which is not included. Claim extraction is syntax-based, not a perfect atomic proposition parser. A future release may add semantic retrieval, provider adapters, richer citation validation, RAG retrieval-set evaluation, experiment tracking, and human annotation. See [`ROADMAP.md`](ROADMAP.md).

## Contributing

Please read [`CONTRIBUTING.md`](CONTRIBUTING.md), run the test/lint commands, and include tests for behavior changes. The project uses the MIT license. See [`CHANGELOG.md`](CHANGELOG.md) for release notes and [`SECURITY.md`](SECURITY.md) for vulnerability reporting.
