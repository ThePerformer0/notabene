"""Domain exceptions for document ingestion in NotaBene.

This module defines the custom exception hierarchy used throughout the
ingestion pipeline to cleanly encapsulate low-level file format, parser,
and I/O errors into structured domain exceptions.
"""

from pathlib import Path


# ---------------------------------------------------------------------------
# PDF Ingestion Exceptions
# ---------------------------------------------------------------------------


class PDFIngestionError(Exception):
    """Base exception for all PDF ingestion failures in NotaBene.

    Attributes:
        path: The file path of the PDF that caused the error (if available).
    """

    def __init__(self, message: str, path: Path | str | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error explanation.
            path: Path to the related PDF file.
        """
        self.path = Path(path) if path is not None else None
        super().__init__(message)


class PDFNotFoundError(PDFIngestionError):
    """Raised when the target PDF file does not exist on disk."""

    def __init__(self, path: Path | str) -> None:
        """Initialize PDFNotFoundError.

        Args:
            path: Path to the missing PDF file.
        """
        self.path = Path(path)
        super().__init__(
            f"PDF file not found at path: {self.path.resolve()}",
            path=self.path,
        )


class PDFCorruptedError(PDFIngestionError):
    """Raised when the file is not a valid PDF or is corrupted and unreadable."""

    def __init__(self, path: Path | str, details: str = "") -> None:
        """Initialize PDFCorruptedError.

        Args:
            path: Path to the corrupted file.
            details: Optional string detailing the underlying parser/system error.
        """
        self.path = Path(path)
        msg = f"Failed to parse corrupted or invalid PDF file: {self.path.resolve()}"
        if details:
            msg = f"{msg} (Details: {details})"
        super().__init__(msg, path=self.path)


class PDFEncryptedError(PDFIngestionError):
    """Raised when the PDF file is password protected or encrypted."""

    def __init__(self, path: Path | str) -> None:
        """Initialize PDFEncryptedError.

        Args:
            path: Path to the encrypted PDF file.
        """
        self.path = Path(path)
        super().__init__(
            f"PDF file is password protected/encrypted and cannot be extracted: {self.path.resolve()}",
            path=self.path,
        )


class PDFEmptyContentError(PDFIngestionError):
    """Raised when a valid PDF contains no extractable text (e.g., scanned image without OCR)."""

    def __init__(self, path: Path | str, page_count: int = 0) -> None:
        """Initialize PDFEmptyContentError.

        Args:
            path: Path to the empty PDF file.
            page_count: Number of pages found in the document.
        """
        self.path = Path(path)
        self.page_count = page_count
        super().__init__(
            f"PDF file contains no extractable text across {page_count} page(s). "
            f"OCR may be required for: {self.path.resolve()}",
            path=self.path,
        )


# ---------------------------------------------------------------------------
# Web Ingestion Exceptions
# ---------------------------------------------------------------------------


class WebIngestionError(Exception):
    """Base exception for all Web ingestion failures in NotaBene.

    Attributes:
        url: Target web URL that caused the error (if available).
    """

    def __init__(self, message: str, url: str | None = None) -> None:
        """Initialize WebIngestionError.

        Args:
            message: Human-readable error explanation.
            url: Target URL string.
        """
        self.url = url
        super().__init__(message)


class InvalidURLError(WebIngestionError):
    """Raised when a provided URL is malformed or uses an unsupported scheme."""

    def __init__(self, url: str, details: str = "") -> None:
        """Initialize InvalidURLError.

        Args:
            url: The invalid URL string.
            details: Optional explanation of why the URL was deemed invalid.
        """
        msg = f"Invalid or malformed URL: '{url}'"
        if details:
            msg = f"{msg} ({details})"
        super().__init__(msg, url=url)


class WebFetchError(WebIngestionError):
    """Raised when downloading a web page fails due to network, timeout, or HTTP errors."""

    def __init__(self, url: str, message: str = "", cause: Exception | None = None) -> None:
        """Initialize WebFetchError.

        Args:
            url: Target web URL.
            message: Context message explaining the fetch failure.
            cause: Optional underlying exception (Timeout, ConnectionError, HTTPError, etc.).
        """
        self.cause = cause
        err_msg = message or "Failed to download web page"
        full_msg = f"{err_msg} for URL: {url}"
        if cause:
            full_msg = f"{full_msg} (Cause: {cause})"
        super().__init__(full_msg, url=url)


class WebEmptyContentError(WebIngestionError):
    """Raised when a web page is successfully fetched but contains no extractable text."""

    def __init__(self, url: str) -> None:
        """Initialize WebEmptyContentError.

        Args:
            url: Target web URL.
        """
        super().__init__(
            f"Web page was fetched successfully but contained no extractable main content: {url}",
            url=url,
        )
