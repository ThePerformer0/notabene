"""Ingestion package for NotaBene: PDF and web content extraction."""

from notabene.ingestion.exceptions import (
    InvalidURLError,
    PDFCorruptedError,
    PDFEmptyContentError,
    PDFEncryptedError,
    PDFIngestionError,
    PDFNotFoundError,
    WebEmptyContentError,
    WebFetchError,
    WebIngestionError,
)
from notabene.ingestion.pdf import (
    ExtractedPDF,
    PDFPage,
    compute_file_hash,
    extract_pdf,
    extract_pdf_pages_lazy,
)
from notabene.ingestion.web import (
    ExtractedWebPage,
    compute_content_hash,
    extract_web_page,
)

__all__ = [
    # PDF Ingestion
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
    # Web Ingestion
    "ExtractedWebPage",
    "extract_web_page",
    "compute_content_hash",
    "WebIngestionError",
    "InvalidURLError",
    "WebFetchError",
    "WebEmptyContentError",
]
