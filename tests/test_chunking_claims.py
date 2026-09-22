from evidencebench.chunking import chunk_documents
from evidencebench.claims import DeterministicClaimExtractor
from evidencebench.models import Document, DocumentPage


def test_markdown_chunk_has_lines_and_section() -> None:
    document = Document(
        identifier="guide.md",
        source_type="markdown",
        path="guide.md",
        text="# Heading\n\nFirst fact.\n\nSecond fact.",
        pages=(DocumentPage("# Heading\n\nFirst fact.\n\nSecond fact."),),
    )
    chunks = chunk_documents((document,))
    assert len(chunks) == 3
    assert chunks[1].location.line_start == 3
    assert chunks[1].location.section == "Heading"


def test_pdf_like_pages_keep_page_location() -> None:
    document = Document(
        identifier="file.pdf",
        source_type="pdf",
        path="file.pdf",
        text="page one\n\npage two",
        pages=(DocumentPage("page one", 1), DocumentPage("page two", 2)),
    )
    chunks = chunk_documents((document,))
    assert [chunk.location.page for chunk in chunks] == [1, 2]
    assert all(chunk.location.line_start is None for chunk in chunks)


def test_long_text_is_bounded() -> None:
    document = Document(
        identifier="a.txt",
        source_type="text",
        path="a.txt",
        text="word " * 200,
        pages=(DocumentPage("word " * 200),),
    )
    chunks = chunk_documents((document,), max_chars=80)
    assert chunks
    assert all(len(chunk.text) <= 80 for chunk in chunks)


def test_claim_extractor_handles_bullets_sentences_and_empty_answer() -> None:
    extractor = DeterministicClaimExtractor()
    claims = extractor.extract("- First fact.\n2. Second fact\n\n# heading")
    assert [claim.text for claim in claims] == ["First fact.", "Second fact", "heading"]
    assert [claim.ordinal for claim in claims] == [1, 2, 3]
    assert extractor.extract("") == ()
