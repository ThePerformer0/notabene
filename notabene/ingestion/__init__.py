"""Ingestion package for NotaBene: PDF and web content extraction."""

from notabene.ingestion.exceptions import (
    PDFCorruptedError,
    PDFEmptyContentError,
    PDFEncryptedError,
    PDFIngestionError,
    PDFNotFoundError,
)
from notabene.ingestion.pdf import (
    ExtractedPDF,
    PDFPage,
    compute_file_hash,
    extract_pdf,
    extract_pdf_pages_lazy,
)

__all__ = [
    "ExtractedPDF",
    "PDFPage",
    "compute_file_hash",
    "extract_pdf",
    "extract_pdf_pages_lazy",
    "PDFIngestionError",
    "PDFNotFoundError",
    "PDFCorruptedError",
    "PDFEncryptedError",
    "PDFEmptyContentError",
]
