from pathlib import Path

import pytest

from evidencebench.chunking import chunk_documents
from evidencebench.errors import ExtractionError, InputError, UnsupportedFormatError
from evidencebench.ingestion import load_documents, normalize_text


def test_text_and_markdown_ingestion_preserves_identifiers_and_text(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a\r\nb\x00", encoding="utf-8")
    (tmp_path / "b.md").write_text("# Heading\n\nbody", encoding="utf-8")
    (tmp_path / "ignored.csv").write_text("not supported", encoding="utf-8")
    docs = load_documents(tmp_path)
    assert [doc.identifier for doc in docs] == ["a.txt", "b.md"]
    assert docs[0].text == "a\nb"
    assert docs[1].source_type == "markdown"


def test_direct_unsupported_file_fails(tmp_path: Path) -> None:
    path = tmp_path / "data.csv"
    path.write_text("x", encoding="utf-8")
    with pytest.raises(UnsupportedFormatError):
        load_documents(path)


def test_empty_directory_and_missing_path_fail(tmp_path: Path) -> None:
    with pytest.raises(InputError):
        load_documents(tmp_path)
    with pytest.raises(InputError):
        load_documents(tmp_path / "missing")


def test_empty_document_is_valid_but_produces_no_chunks(tmp_path: Path) -> None:
    path = tmp_path / "empty.txt"
    path.write_text("", encoding="utf-8")
    documents = load_documents(path)
    assert documents[0].text == ""
    assert chunk_documents(documents) == ()


def test_size_limit_and_symlink_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "large.txt"
    path.write_text("12345", encoding="utf-8")
    with pytest.raises(InputError):
        load_documents(path, max_file_bytes=2)
    link = tmp_path / "link.txt"
    try:
        link.symlink_to(path)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks are not available")
    with pytest.raises(InputError):
        load_documents(link)


def test_invalid_utf8_is_reported(tmp_path: Path) -> None:
    path = tmp_path / "bad.txt"
    path.write_bytes(b"\xff")
    with pytest.raises(ExtractionError):
        load_documents(path)


def test_normalize_text() -> None:
    assert normalize_text(" a\r\nb\x00 ") == "a\nb"
