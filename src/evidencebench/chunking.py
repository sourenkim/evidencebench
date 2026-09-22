"""Deterministic paragraph/line chunking with best-effort locations."""

from __future__ import annotations

import re

from .ingestion import section_for_line
from .models import Chunk, Document, DocumentPage, SourceLocation


def _units(text: str) -> list[tuple[str, int, int]]:
    """Return non-empty paragraph units and their one-based line range."""
    if not text.strip():
        return []
    lines = text.splitlines()
    result: list[tuple[str, int, int]] = []
    start: int | None = None
    buffer: list[str] = []
    for index, line in enumerate(lines, start=1):
        if line.strip():
            if start is None:
                start = index
            buffer.append(line.strip())
        elif buffer and start is not None:
            result.append((" ".join(buffer), start, index - 1))
            start, buffer = None, []
    if buffer and start is not None:
        result.append((" ".join(buffer), start, len(lines)))
    return result


def _split_long(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    sentences = re.split(r"(?<=[.!?])\s+", text)
    pieces: list[str] = []
    current = ""
    for sentence in sentences:
        if not sentence:
            continue
        candidate = f"{current} {sentence}".strip()
        if current and len(candidate) > max_chars:
            pieces.append(current)
            current = sentence
        else:
            current = candidate
    if current:
        pieces.append(current)
    # A sentence can itself be oversized; hard split it as a final safety bound.
    bounded: list[str] = []
    for piece in pieces:
        bounded.extend(
            piece[index : index + max_chars] for index in range(0, len(piece), max_chars)
        )
    return bounded


def _page_chunks(
    document: Document,
    page: DocumentPage,
    page_index: int,
    max_chars: int,
) -> list[Chunk]:
    units = _units(page.text)
    chunks: list[Chunk] = []
    if not units and page.text.strip():
        units = [(page.text.strip(), 1, max(1, len(page.text.splitlines())))]
    for unit_text, start, end in units:
        parts = _split_long(unit_text, max_chars)
        for _part_index, part in enumerate(parts):
            # For a hard split, the exact line boundary is not knowable; retain the
            # paragraph's line range rather than fabricating a more precise location.
            location = SourceLocation(
                page=page.page_number,
                line_start=None if page.page_number is not None else start,
                line_end=None if page.page_number is not None else end,
                section=(
                    None
                    if page.page_number is not None
                    else section_for_line(page.text.splitlines(), start)
                ),
            )
            chunk_id = f"{document.identifier}#chunk-{page_index + 1}-{len(chunks) + 1}"
            chunks.append(
                Chunk(
                    identifier=chunk_id,
                    document_id=document.identifier,
                    text=part,
                    location=location,
                    source_type=document.source_type,
                )
            )
    return chunks


def chunk_documents(documents: tuple[Document, ...], *, max_chars: int = 700) -> tuple[Chunk, ...]:
    """Create stable chunks; PDF pages are never combined across page boundaries."""
    if max_chars < 80:
        raise ValueError("max_chars must be at least 80")
    chunks: list[Chunk] = []
    for document in documents:
        pages = document.pages or (DocumentPage(document.text),)
        for page_index, page in enumerate(pages):
            chunks.extend(_page_chunks(document, page, page_index, max_chars))
    return tuple(chunks)
