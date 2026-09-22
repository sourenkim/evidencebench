"""Safe, local document ingestion for the supported MVP formats."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from .errors import ExtractionError, InputError, UnsupportedFormatError
from .models import Document, DocumentPage

SUPPORTED_EXTENSIONS = {".txt", ".md", ".markdown", ".pdf"}
DEFAULT_MAX_FILE_BYTES = 10 * 1024 * 1024


def normalize_text(text: str) -> str:
    """Normalize line endings and harmless Unicode variation without rewriting content."""
    text = text.replace("\x00", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return unicodedata.normalize("NFKC", text).strip()


def _source_files(source_path: Path) -> list[Path]:
    if not source_path.exists():
        raise InputError(f"Sources path does not exist: {source_path}")
    if source_path.is_symlink():
        raise InputError("A symlink cannot be used as the sources root")
    if source_path.is_file():
        return [source_path]
    if not source_path.is_dir():
        raise InputError(f"Sources path is not a regular file or directory: {source_path}")
    files = [
        path
        for path in sorted(source_path.rglob("*"))
        if path.is_file() and not path.is_symlink() and not path.name.startswith(".")
    ]
    return files


def _relative_identifier(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name


def _load_text(path: Path, identifier: str, source_type: str, max_bytes: int) -> Document:
    size = path.stat().st_size
    if size > max_bytes:
        raise InputError(
            f"Refusing {path.name}: file is {size} bytes, above the {max_bytes}-byte limit"
        )
    try:
        text = normalize_text(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        raise ExtractionError(f"{path.name} is not valid UTF-8 text") from exc
    return Document(
        identifier=identifier,
        source_type=source_type,
        text=text,
        path=str(path),
        pages=(DocumentPage(text=text),),
    )


def _load_pdf(path: Path, identifier: str, max_bytes: int) -> Document:
    if path.stat().st_size > max_bytes:
        raise InputError(f"Refusing {path.name}: file exceeds the {max_bytes}-byte limit")
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ExtractionError(
            "PDF support requires pypdf. Install it with `pip install 'evidencebench[pdf]'`."
        ) from exc
    try:
        reader = PdfReader(str(path), strict=False)
        pages = tuple(
            DocumentPage(text=normalize_text(page.extract_text() or ""), page_number=index)
            for index, page in enumerate(reader.pages, start=1)
        )
    except Exception as exc:  # pypdf exposes several parser-specific exception types.
        raise ExtractionError(f"Could not extract PDF {path.name}: {exc}") from exc
    text = "\n\n".join(page.text for page in pages if page.text)
    return Document(
        identifier=identifier,
        source_type="pdf",
        text=text,
        path=str(path),
        pages=pages,
        metadata={"page_count": len(pages)},
    )


def load_documents(
    sources: str | Path,
    *,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
) -> tuple[Document, ...]:
    """Load supported files from a file or directory in stable path order.

    Unsupported files are ignored in a directory so a source folder can contain
    README files or unrelated assets. A directly supplied unsupported file is an
    error, which catches typos early.
    """
    root = Path(sources).expanduser()
    files = _source_files(root)
    if root.is_file() and root.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFormatError(
            f"Unsupported source format {root.suffix or '<no extension>'}; "
            "choose TXT, Markdown, or PDF"
        )
    supported = [path for path in files if path.suffix.lower() in SUPPORTED_EXTENSIONS]
    if not supported:
        raise InputError(f"No TXT, Markdown, or PDF files found under {root}")
    root_for_ids = root if root.is_dir() else root.parent
    documents: list[Document] = []
    for path in supported:
        identifier = _relative_identifier(path, root_for_ids)
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            documents.append(_load_pdf(path, identifier, max_file_bytes))
        else:
            source_type = "markdown" if suffix in {".md", ".markdown"} else "text"
            documents.append(_load_text(path, identifier, source_type, max_file_bytes))
    return tuple(documents)


def line_number_at(text: str, offset: int) -> int:
    """Return a one-based line number for an offset, including empty text."""
    return text.count("\n", 0, max(offset, 0)) + 1


def section_for_line(lines: list[str], line_number: int) -> str | None:
    """Find the closest Markdown heading above a line, if any."""
    heading: str | None = None
    for line in lines[:line_number]:
        match = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if match:
            heading = match.group(1).strip()
    return heading
