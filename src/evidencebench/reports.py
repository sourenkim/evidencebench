"""Terminal, JSON, and standalone HTML report renderers."""

from __future__ import annotations

import html
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import EvaluationResult


def _pct(value: float) -> str:
    return f"{value:.1%}"


def render_terminal(result: EvaluationResult) -> str:
    m = result.metrics
    lines = [
        "EvidenceBench Evaluation",
        "=" * 26,
        f"Status: {result.status.value}",
        f"Claims: {m.total_claims}",
        f"Supported: {m.supported}",
        f"Partially supported: {m.partially_supported}",
        f"Unsupported: {m.unsupported}",
        f"Insufficient evidence: {m.insufficient_evidence}",
        "",
        f"Evidence coverage (fully supported): {_pct(m.evidence_coverage)}",
        f"Unsupported claim rate: {_pct(m.unsupported_claim_rate)}",
        f"Partial support rate: {_pct(m.partial_support_rate)}",
        f"Citation coverage: {_pct(m.citation_coverage)}",
        f"Evidence retrieval rate: {_pct(m.evidence_retrieval_rate)}",
        "",
        "Claim details",
        "------------",
    ]
    for item in result.claims:
        lines.extend(
            [
                f"#{item.claim.ordinal} [{item.status.value}] {item.claim.text}",
                f"  Reason: {item.rationale}",
            ]
        )
        if item.evidence:
            for evidence in item.evidence:
                location = _location_label(evidence.location.to_dict())
                lines.append(
                    f"  Evidence: {evidence.document_id} {location} "
                    f"(score {evidence.relevance_score:.2f})"
                )
                lines.append(f"    {evidence.text}")
        else:
            lines.append("  Evidence: No adequate supporting evidence found.")
    return "\n".join(lines)


def _location_label(location: dict[str, Any]) -> str:
    parts: list[str] = []
    if location.get("page") is not None:
        parts.append(f"page {location['page']}")
    if location.get("line_start") is not None:
        end = location.get("line_end") or location["line_start"]
        parts.append(f"lines {location['line_start']}-{end}")
    if location.get("section"):
        parts.append(f"section {location['section']}")
    return f"({', '.join(parts)})" if parts else "(location unavailable)"


def render_json(result: EvaluationResult) -> str:
    return json.dumps(result.to_dict(), indent=2, ensure_ascii=False) + "\n"


def render_html(result: EvaluationResult) -> str:
    m = result.metrics
    metric_rows = "".join(
        f"<tr><th>{html.escape(label)}</th><td>{html.escape(value)}</td></tr>"
        for label, value in (
            ("Total claims", str(m.total_claims)),
            ("Supported", str(m.supported)),
            ("Partially supported", str(m.partially_supported)),
            ("Unsupported", str(m.unsupported)),
            ("Insufficient evidence", str(m.insufficient_evidence)),
            ("Evidence coverage (fully supported)", _pct(m.evidence_coverage)),
            ("Citation coverage", _pct(m.citation_coverage)),
            ("Evidence retrieval rate", _pct(m.evidence_retrieval_rate)),
        )
    )
    claim_sections: list[str] = []
    for item in result.claims:
        evidence_html = "".join(
            "<li><strong>"
            + html.escape(evidence.document_id)
            + "</strong> "
            + html.escape(_location_label(evidence.location.to_dict()))
            + f" <small>score {evidence.relevance_score:.2f}</small>"
            + f"<blockquote>{html.escape(evidence.text)}</blockquote></li>"
            for evidence in item.evidence
        )
        if not evidence_html:
            evidence_html = "<li>No adequate supporting evidence found.</li>"
        claim_sections.append(
            f"<article class='claim {item.status.value.lower()}'>"
            f"<h3>Claim #{item.claim.ordinal} "
            f"<span class='badge'>{html.escape(item.status.value)}</span></h3>"
            f"<p><strong>Claim:</strong> {html.escape(item.claim.text)}</p>"
            f"<p><strong>Reason:</strong> {html.escape(item.rationale)}</p>"
            f"<p><strong>Evidence:</strong></p><ul>{evidence_html}</ul></article>"
        )
    generated = datetime.now(UTC).isoformat()
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>EvidenceBench evaluation</title>
<style>
body{{font:16px/1.5 system-ui,sans-serif;max-width:1000px;margin:2rem auto;padding:0 1rem;color:#172033;background:#f7f8fb}}
h1,h2,h3{{line-height:1.2}} table{{border-collapse:collapse;background:white;width:100%;max-width:650px}}
th,td{{padding:.55rem .7rem;border:1px solid #d8dce6;text-align:left}} th{{width:55%}}
.claim{{background:white;border-left:5px solid #8792a6;padding:.75rem 1rem;margin:1rem 0;box-shadow:0 1px 3px #0001}}
.supported{{border-color:#238636}} .partially_supported{{border-color:#b58105}} .unsupported{{border-color:#cf222e}} .insufficient_evidence{{border-color:#8250df}}
.badge{{font-size:.75rem;border:1px solid #ccd2dd;border-radius:999px;padding:.2rem .5rem;vertical-align:middle}}
blockquote{{margin:.5rem 0;padding:.5rem .75rem;border-left:3px solid #ccd2dd;background:#f3f5f8;white-space:pre-wrap}}
small,footer{{color:#596579}} .answer{{white-space:pre-wrap;background:white;padding:1rem}}
</style></head><body>
<h1>EvidenceBench Evaluation</h1><p><strong>Status:</strong> {html.escape(result.status.value)}</p>
<h2>Overview</h2><table>{metric_rows}</table>
<h2>Question</h2><p>{html.escape(result.question)}</p>
<h2>Answer</h2><div class="answer">{html.escape(result.answer)}</div>
<h2>Claim details</h2>{"".join(claim_sections)}
<footer>Generated by EvidenceBench 0.1.0 at {html.escape(generated)}. Heuristic confidence is not factual certainty.</footer>
</body></html>
"""


def write_report(result: EvaluationResult, output: str | Path, format: str) -> Path:
    """Write a report to a file or an output directory and return its path."""
    target = Path(output)
    suffix = {"json": ".json", "html": ".html", "terminal": ".txt"}[format]
    if (
        (target.exists() and target.is_dir())
        or target.suffix == ""
        or str(target).endswith(("/", "\\"))
    ):
        target.mkdir(parents=True, exist_ok=True)
        target = target / f"evaluation{suffix}"
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
    content = {"json": render_json, "html": render_html, "terminal": render_terminal}[format](
        result
    )
    target.write_text(content, encoding="utf-8")
    return target
