from pathlib import Path

import pytest

from evidencebench.errors import ExtractionError
from evidencebench.ingestion import load_documents


def test_pdf_without_dependency_has_actionable_error(tmp_path: Path) -> None:
    path = tmp_path / "file.pdf"
    path.write_bytes(b"not a real pdf")
    try:
        import pypdf  # noqa: F401
    except ImportError:
        with pytest.raises(Exception, match="pypdf"):
            load_documents(path)
    else:
        # The installed parser should still fail clearly for malformed content.
        with pytest.raises(ExtractionError):
            load_documents(path)
