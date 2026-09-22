from pathlib import Path

from evidencebench.chunking import chunk_documents
from evidencebench.evaluation import evaluate_answer
from evidencebench.models import Document, DocumentPage
from evidencebench.reports import render_html, render_json, render_terminal, write_report


def result():
    text = "# Heading\n\nThe safe item is blue."
    doc = Document("source.md", "markdown", text, "source.md", (DocumentPage(text),))
    return evaluate_answer("What color?", "The safe item is blue.", chunk_documents((doc,)))


def test_renderers_include_claim_and_escape_html() -> None:
    evaluation = result()
    assert "SUPPORTED" in render_terminal(evaluation)
    assert '"metrics"' in render_json(evaluation)
    malicious = evaluation.__class__(
        "<script>alert(1)</script>",
        "<img src=x>",
        evaluation.claims,
        evaluation.metrics,
        evaluation.status,
    )
    output = render_html(malicious)
    assert "&lt;script&gt;" in output
    assert "<script>alert(1)</script>" not in output
    assert "<img src=x>" not in output
    assert "<article" in output


def test_write_report_supports_directory_and_file(tmp_path: Path) -> None:
    evaluation = result()
    directory = tmp_path / "reports"
    html_path = write_report(evaluation, directory, "html")
    assert html_path.name == "evaluation.html"
    assert html_path.exists()
    json_path = write_report(evaluation, tmp_path / "out.json", "json")
    assert json_path.name == "out.json"
    assert '"schema_version"' in json_path.read_text(encoding="utf-8")
