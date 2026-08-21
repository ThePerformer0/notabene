"""Unit tests for notabene.ingestion.pdf module.

All test PDF documents are generated programmatically using PyMuPDF (fitz)
inside pytest fixtures to avoid checking in binary test assets.
"""

from datetime import timezone
import inspect
from pathlib import Path

import fitz
import pytest

from notabene.ingestion.exceptions import (
    PDFCorruptedError,
    PDFEmptyContentError,
    PDFEncryptedError,
    PDFNotFoundError,
)
from notabene.ingestion.pdf import (
    ExtractedPDF,
    PDFPage,
    compute_file_hash,
    extract_pdf,
    extract_pdf_pages_lazy,
)


@pytest.fixture
def valid_pdf_with_metadata(tmp_path: Path) -> Path:
    """Create a valid 2-page PDF with defined title and author metadata."""
    pdf_path = tmp_path / "valid_with_meta.pdf"
    doc = fitz.open()

    p1 = doc.new_page()
    p1.insert_text((50, 72), "Introduction to Academic Search Engines.\nFirst page content.")

    p2 = doc.new_page()
    p2.insert_text((50, 72), "Methodology and Retrieval Models.\nSecond page content.")

    doc.set_metadata(
        {
            "title": "Quantum Computing & Local RAG Systems",
            "author": "Dr. Ada Lovelace",
        }
    )
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


@pytest.fixture
def valid_pdf_without_metadata(tmp_path: Path) -> Path:
    """Create a valid 1-page PDF without title or author metadata."""
    pdf_path = tmp_path / "valid_no_meta.pdf"
    doc = fitz.open()
    p = doc.new_page()
    p.insert_text((50, 72), "Unstructured plain document without document headers.")
    doc.set_metadata({})
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


@pytest.fixture
def empty_content_pdf(tmp_path: Path) -> Path:
    """Create a valid 2-page PDF containing only blank white pages (no extractable text)."""
    pdf_path = tmp_path / "empty_pages.pdf"
    doc = fitz.open()
    doc.new_page()  # Page 1 empty
    doc.new_page()  # Page 2 empty
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


@pytest.fixture
def encrypted_pdf(tmp_path: Path) -> Path:
    """Create a password-protected PDF document."""
    pdf_path = tmp_path / "encrypted.pdf"
    doc = fitz.open()
    p = doc.new_page()
    p.insert_text((50, 72), "Highly classified research report.")
    doc.save(
        str(pdf_path),
        encryption=fitz.PDF_ENCRYPT_AES_256,
        user_pw="correct_password",
        owner_pw="admin_password",
    )
    doc.close()
    return pdf_path


@pytest.fixture
def corrupted_pdf_file(tmp_path: Path) -> Path:
    """Create an invalid corrupted file with a .pdf extension."""
    pdf_path = tmp_path / "corrupted.pdf"
    pdf_path.write_text("This is plain text and definitely not a valid binary PDF document.")
    return pdf_path


# ---------------------------------------------------------------------------
# Test Cases
# ---------------------------------------------------------------------------


def test_extract_pdf_valid_returns_correct_metadata(valid_pdf_with_metadata: Path) -> None:
    """Test extracting a valid 2-page PDF with complete title and author metadata."""
    extracted = extract_pdf(valid_pdf_with_metadata)

    assert isinstance(extracted, ExtractedPDF)
    assert extracted.source_path == valid_pdf_with_metadata.resolve()
    assert extracted.title == "Quantum Computing & Local RAG Systems"
    assert extracted.author == "Dr. Ada Lovelace"
    assert extracted.page_count == 2
    assert len(extracted.pages) == 2

    # Verify page 1
    assert extracted.pages[0].number == 1
    assert "Introduction to Academic Search Engines" in extracted.pages[0].text
    assert extracted.pages[0].char_count == len(extracted.pages[0].text)

    # Verify page 2
    assert extracted.pages[1].number == 2
    assert "Methodology and Retrieval Models" in extracted.pages[1].text
    assert extracted.pages[1].char_count == len(extracted.pages[1].text)

    # Verify hash and timestamp
    assert len(extracted.file_hash) == 64
    assert extracted.extracted_at.tzinfo == timezone.utc


def test_extract_pdf_missing_metadata_returns_none(valid_pdf_without_metadata: Path) -> None:
    """Test that a PDF without metadata fields yields None for title and author."""
    extracted = extract_pdf(valid_pdf_without_metadata)

    assert extracted.title is None
    assert extracted.author is None
    assert extracted.page_count == 1
    assert len(extracted.pages) == 1
    assert "Unstructured plain document" in extracted.pages[0].text


def test_extract_pdf_nonexistent_file_raises(tmp_path: Path) -> None:
    """Test that targeting a non-existent file raises PDFNotFoundError."""
    missing_path = tmp_path / "does_not_exist_at_all.pdf"

    with pytest.raises(PDFNotFoundError) as exc_info:
        extract_pdf(missing_path)

    assert str(missing_path.resolve()) in str(exc_info.value)
    assert exc_info.value.path == missing_path


def test_extract_pdf_corrupted_file_raises(corrupted_pdf_file: Path) -> None:
    """Test that opening a non-PDF corrupted file raises PDFCorruptedError."""
    with pytest.raises(PDFCorruptedError) as exc_info:
        extract_pdf(corrupted_pdf_file)

    assert str(corrupted_pdf_file.resolve()) in str(exc_info.value)
    assert exc_info.value.path == corrupted_pdf_file


def test_extract_pdf_empty_content_raises(empty_content_pdf: Path) -> None:
    """Test that a valid PDF with blank pages raises PDFEmptyContentError."""
    with pytest.raises(PDFEmptyContentError) as exc_info:
        extract_pdf(empty_content_pdf)

    assert exc_info.value.page_count == 2
    assert "OCR may be required" in str(exc_info.value)
    assert exc_info.value.path == empty_content_pdf


def test_extract_pdf_encrypted_raises(encrypted_pdf: Path) -> None:
    """Test that an encrypted PDF raises PDFEncryptedError."""
    with pytest.raises(PDFEncryptedError) as exc_info:
        extract_pdf(encrypted_pdf)

    assert str(encrypted_pdf.resolve()) in str(exc_info.value)
    assert exc_info.value.path == encrypted_pdf


def test_extract_pdf_pages_lazy_is_generator(valid_pdf_with_metadata: Path) -> None:
    """Verify that extract_pdf_pages_lazy returns a generator and yields items lazily."""
    gen = extract_pdf_pages_lazy(valid_pdf_with_metadata)

    assert inspect.isgenerator(gen)

    # Consume first page only
    first_page = next(gen)
    assert isinstance(first_page, PDFPage)
    assert first_page.number == 1
    assert "Introduction to Academic Search Engines" in first_page.text

    # Consume second page
    second_page = next(gen)
    assert isinstance(second_page, PDFPage)
    assert second_page.number == 2

    # Generator should now be exhausted
    with pytest.raises(StopIteration):
        next(gen)


def test_compute_file_hash_deterministic(valid_pdf_with_metadata: Path, tmp_path: Path) -> None:
    """Verify deterministic hash computation for identical and different files."""
    hash1 = compute_file_hash(valid_pdf_with_metadata)
    hash2 = compute_file_hash(valid_pdf_with_metadata)

    # Determinism
    assert hash1 == hash2
    assert len(hash1) == 64

    # Different content produces different hash
    other_file = tmp_path / "other.pdf"
    other_file.write_bytes(b"%PDF-1.4 dummy header binary stream")
    other_hash = compute_file_hash(other_file)

    assert hash1 != other_hash


def test_full_text_matches_concatenated_pages(valid_pdf_with_metadata: Path) -> None:
    """Verify that full_text is coherent with the concatenation of all individual page texts."""
    extracted = extract_pdf(valid_pdf_with_metadata)

    expected_full_text = "\n\n".join(page.text for page in extracted.pages)
    assert extracted.full_text == expected_full_text

    for page in extracted.pages:
        assert page.text in extracted.full_text


def test_extract_pdf_unexpected_exception_propagates(
    valid_pdf_with_metadata: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that unexpected exceptions (e.g. MemoryError) are not converted to PDFCorruptedError."""

    def mock_open(*args: object, **kwargs: object) -> None:
        raise MemoryError("Out of memory during low-level allocation")

    monkeypatch.setattr(fitz, "open", mock_open)

    with pytest.raises(MemoryError):
        extract_pdf(valid_pdf_with_metadata)
