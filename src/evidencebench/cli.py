"""Command-line interface for EvidenceBench."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .benchmark import render_benchmark_terminal, run_benchmark, validate_benchmark
from .chunking import chunk_documents
from .errors import EvidenceBenchError, InputError
from .evaluation import evaluate_answer
from .ingestion import load_documents
from .metrics import check_thresholds
from .models import EvaluationResult, Thresholds
from .reports import render_html, render_json, render_terminal, write_report


def _read_input(path_value: str, label: str) -> str:
    path = Path(path_value).expanduser()
    if not path.is_file():
        raise InputError(f"{label} file does not exist: {path}")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise InputError(f"{label} file is not valid UTF-8: {path}") from exc


def _add_evaluation_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--sources", required=True, help="TXT/Markdown/PDF file or directory")
    parser.add_argument("--question", required=True, help="UTF-8 text file containing the question")
    parser.add_argument("--answer", required=True, help="UTF-8 text file containing the AI answer")
    parser.add_argument("--format", choices=("terminal", "json", "html"), default="terminal")
    parser.add_argument("--output", help="Output file or directory; stdout is used when omitted")
    parser.add_argument("--top-k", type=int, default=3, help="Maximum evidence snippets per claim")
    parser.add_argument(
        "--min-relevance", type=float, default=0.15, help="Retrieval score threshold"
    )


def _build_result(args: argparse.Namespace) -> EvaluationResult:
    documents = load_documents(args.sources)
    chunks = chunk_documents(documents)
    if args.top_k < 1:
        raise InputError("--top-k must be positive")
    if not 0 <= args.min_relevance <= 1:
        raise InputError("--min-relevance must be between 0 and 1")
    # Construct the retriever explicitly so CLI options are part of the reportable behavior.
    from .retrieval import LexicalRetriever

    question = _read_input(args.question, "Question")
    answer = _read_input(args.answer, "Answer")
    result = evaluate_answer(
        question,
        answer,
        chunks,
        retriever=LexicalRetriever(chunks, top_k=args.top_k, min_score=args.min_relevance),
    )
    return result


def _render_or_write(result: EvaluationResult, format_name: str, output: str | None) -> None:
    if output:
        path = write_report(result, output, format_name)
        print(f"Wrote {format_name} report to {path}")
        return
    renderer = {"terminal": render_terminal, "json": render_json, "html": render_html}[format_name]
    print(renderer(result), end="" if format_name != "html" else "\n")


def _run_evaluate(args: argparse.Namespace) -> int:
    result = _build_result(args)
    _render_or_write(result, args.format, args.output)
    return 0


def _run_assert(args: argparse.Namespace) -> int:
    result = _build_result(args)
    thresholds = Thresholds(
        minimum_evidence_coverage=args.minimum_evidence_coverage,
        maximum_unsupported_rate=args.maximum_unsupported_rate,
        maximum_partial_rate=args.maximum_partial_rate,
    )
    violations = check_thresholds(result.metrics, thresholds)
    _render_or_write(result, args.format, args.output)
    if violations:
        print("Threshold failures:", file=sys.stderr)
        for violation in violations:
            print(
                f"- {violation.metric}={violation.actual:.3f} "
                f"does not satisfy {violation.operator} {violation.threshold:.3f}",
                file=sys.stderr,
            )
        return 1
    return 0


def _run_validate(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if (path / "documents").is_dir() and (path / "cases").is_dir():
        count = validate_benchmark(path)
        print(f"Valid benchmark: {count} cases")
    else:
        documents = load_documents(path)
        print(f"Valid sources: {len(documents)} documents")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="evidencebench",
        description="Measure whether AI-generated claims are supported by source documents.",
    )
    parser.add_argument("--version", action="version", version=f"EvidenceBench {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    evaluate_parser = subparsers.add_parser("evaluate", help="Evaluate one question and answer")
    _add_evaluation_arguments(evaluate_parser)
    evaluate_parser.set_defaults(handler=_run_evaluate)

    assert_parser = subparsers.add_parser("assert", help="Evaluate and enforce CI thresholds")
    _add_evaluation_arguments(assert_parser)
    assert_parser.add_argument("--minimum-evidence-coverage", type=float)
    assert_parser.add_argument("--maximum-unsupported-rate", type=float)
    assert_parser.add_argument("--maximum-partial-rate", type=float)
    assert_parser.set_defaults(handler=_run_assert)

    benchmark_parser = subparsers.add_parser(
        "benchmark", help="Run the reproducible local benchmark"
    )
    benchmark_parser.add_argument(
        "path", help="Benchmark directory containing documents/ and cases/"
    )
    benchmark_parser.add_argument("--format", choices=("terminal", "json"), default="terminal")
    benchmark_parser.add_argument("--output", help="Output file")
    benchmark_parser.set_defaults(handler=_run_benchmark)

    validate_parser = subparsers.add_parser(
        "validate", help="Validate sources or a benchmark directory"
    )
    validate_parser.add_argument("path")
    validate_parser.set_defaults(handler=_run_validate)

    version_parser = subparsers.add_parser("version", help="Print the package version")
    version_parser.set_defaults(handler=lambda _args: print(__version__) or 0)
    return parser


def _run_benchmark(args: argparse.Namespace) -> int:
    summary = run_benchmark(args.path)
    content = (
        render_benchmark_terminal(summary)
        if args.format == "terminal"
        else json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
    )
    if args.output:
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        print(f"Wrote {args.format} benchmark report to {target}")
    else:
        print(content, end="")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except EvidenceBenchError as exc:
        print(f"evidencebench: error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"evidencebench: filesystem error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
