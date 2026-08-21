"""Robust and high-performance PDF extraction module for NotaBene.

This module provides functions and data structures for extracting plain text,
page-by-page content, and document metadata from PDF files using PyMuPDF (fitz).
It is designed strictly for extraction: no summarization, OCR, or embedding logic.
"""

from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import logging
from pathlib import Path

import fitz

from notabene.ingestion.exceptions import (
    PDFCorruptedError,
    PDFEmptyContentError,
    PDFEncryptedError,
    PDFNotFoundError,
)

# Disable low-level MuPDF stderr warnings to prevent noise outside logging
fitz.TOOLS.mupdf_display_errors(False)

logger = logging.getLogger("notabene.ingestion.pdf")

_HASH_CHUNK_SIZE: int = 65536


@dataclass(frozen=True)
class PDFPage:
    """Represents a single extracted PDF page.

    Attributes:
        number: 1-indexed page number in the document.
        text: Raw extracted textual content of the page.
        char_count: Total number of characters in the page text.
    """

    number: int
    text: str
    char_count: int


@dataclass(frozen=True)
class ExtractedPDF:
    """Structured representation of an extracted PDF document.

    Attributes:
        source_path: Path to the source PDF file on disk.
        title: Title of the document from metadata, or None if missing.
        author: Author of the document from metadata, or None if missing.
        page_count: Total number of pages in the document.
        pages: List of individual extracted pages.
        full_text: Concatenation of all page texts joined by double newlines.
        file_hash: Hexadecimal SHA-256 digest of the raw PDF file.
        extracted_at: UTC timestamp when the extraction was performed.
    """

    source_path: Path
    title: str | None
    author: str | None
    page_count: int
    pages: list[PDFPage]
    full_text: str
    file_hash: str
    extracted_at: datetime


def compute_file_hash(path: Path | str) -> str:
    """Compute the SHA-256 checksum of a file by reading it in fixed chunks.

    Args:
        path: Path to the target file.

    Returns:
        Hexadecimal SHA-256 string representation of the file.

    Raises:
        PDFNotFoundError: If the file does not exist.
        PDFCorruptedError: If the file cannot be read due to an I/O error.
    """
    file_path = Path(path)
    if not file_path.is_file():
        logger.warning("Hash computation failed: file does not exist at %s", file_path)
        raise PDFNotFoundError(file_path)

    hasher = hashlib.sha256()
    try:
        with file_path.open("rb") as f:
            while chunk := f.read(_HASH_CHUNK_SIZE):
                hasher.update(chunk)
    except OSError as err:
        logger.warning("I/O failure while hashing file %s: %s", file_path, err)
        raise PDFCorruptedError(file_path, details=f"I/O error during hashing: {err}") from err

    digest = hasher.hexdigest()
    logger.debug("Computed SHA-256 for %s: %s", file_path, digest)
    return digest


def _clean_metadata_field(value: str | None) -> str | None:
    """Clean and normalize a metadata string value.

    Args:
        value: Raw metadata field string value or None.

    Returns:
        Stripped string if non-empty, otherwise None.
    """
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned if cleaned else None


def _open_pdf(path: Path | str) -> tuple[Path, fitz.Document]:
    """Open and validate a PDF document with PyMuPDF.

    Args:
        path: Path to the PDF file.

    Returns:
        A tuple of (resolved Path, fitz.Document instance).

    Raises:
        PDFNotFoundError: If the file does not exist on disk.
        PDFCorruptedError: If the file is not a valid PDF or is corrupted.
        PDFEncryptedError: If the PDF is password-protected or encrypted.
    """
    file_path = Path(path)
    if not file_path.is_file():
        logger.warning("Target PDF does not exist: %s", file_path)
        raise PDFNotFoundError(file_path)

    try:
        doc = fitz.open(file_path)
    except (fitz.FileDataError, fitz.EmptyFileError, RuntimeError) as err:
        logger.warning("PyMuPDF failed to parse %s: %s", file_path, err)
        raise PDFCorruptedError(file_path, details=str(err)) from err

    if doc.is_encrypted or doc.needs_pass:
        doc.close()
        logger.warning("PDF is password-protected/encrypted: %s", file_path)
        raise PDFEncryptedError(file_path)

    return file_path, doc


def extract_pdf(path: Path | str) -> ExtractedPDF:
    """Extract complete text and metadata from a PDF file.

    Args:
        path: Path to the PDF file.

    Returns:
        An ExtractedPDF dataclass instance containing all extracted data.

    Raises:
        PDFNotFoundError: If the file does not exist.
        PDFCorruptedError: If the file is corrupted or not a valid PDF.
        PDFEncryptedError: If the file is password-protected or encrypted.
        PDFEmptyContentError: If the PDF contains no extractable text across all pages.
    """
    file_path, doc = _open_pdf(path)
    logger.debug("Beginning extraction of PDF: %s (page_count=%d)", file_path, len(doc))

    try:
        raw_meta = doc.metadata or {}
        title = _clean_metadata_field(raw_meta.get("title"))
        author = _clean_metadata_field(raw_meta.get("author"))

        pages: list[PDFPage] = []
        has_non_empty_content = False

        for idx, page in enumerate(doc):
            page_text = page.get_text()
            char_count = len(page_text)
            if page_text.strip():
                has_non_empty_content = True

            pages.append(
                PDFPage(
                    number=idx + 1,
                    text=page_text,
                    char_count=char_count,
                )
            )

        if not has_non_empty_content:
            logger.warning(
                "PDF %s opened successfully with %d page(s) but contains no extractable text",
                file_path,
                len(pages),
            )
            raise PDFEmptyContentError(file_path, page_count=len(pages))

        full_text = "\n\n".join(p.text for p in pages)
        file_hash = compute_file_hash(file_path)
        extracted_at = datetime.now(timezone.utc)

        logger.debug(
            "Successfully extracted %d page(s) (%d total chars) from %s",
            len(pages),
            len(full_text),
            file_path,
        )

        return ExtractedPDF(
            source_path=file_path.resolve(),
            title=title,
            author=author,
            page_count=len(pages),
            pages=pages,
            full_text=full_text,
            file_hash=file_hash,
            extracted_at=extracted_at,
        )
    finally:
        doc.close()


def extract_pdf_pages_lazy(path: Path | str) -> Iterator[PDFPage]:
    """Stream PDF pages lazily without loading the entire document text into memory.

    This generator is suitable for large PDF documents (>500 pages) where
    streaming is preferred over complete in-memory representations.

    Args:
        path: Path to the PDF file.

    Yields:
        PDFPage objects for each page in document order.

    Raises:
        PDFNotFoundError: If the file does not exist.
        PDFCorruptedError: If the file is corrupted or not a valid PDF.
        PDFEncryptedError: If the file is password-protected or encrypted.
    """
    file_path, doc = _open_pdf(path)
    logger.debug("Streaming pages lazily from PDF: %s (page_count=%d)", file_path, len(doc))

    try:
        for idx, page in enumerate(doc):
            page_text = page.get_text()
            yield PDFPage(
                number=idx + 1,
                text=page_text,
                char_count=len(page_text),
            )
    finally:
        doc.close()
        logger.debug("Closed PDF document stream for: %s", file_path)
