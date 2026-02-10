"""Management of PDF documents."""
from pathlib import Path
import shutil
import logging
from typing import List, Optional

import pdfplumber
from sqlalchemy.orm import Session

from notabene.models.pdf import PDFDocument
from notabene.core.config import get_config

logger = logging.getLogger(__name__)


class DocumentManager:
    """Manager for PDF documents."""

    def __init__(self, session: Session):
        """
        Initialize the manager.

        Args:
            session: Database session
        """
        self.session = session
        self.config = get_config()
        self.storage_path = self.config.pdf_directory
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def add_pdf(self, file_path: str | Path, auto_extract: bool = True) -> PDFDocument:
        """
        Add a PDF to the database.

        Args:
            file_path: Path to the PDF file
            auto_extract: Whether to automatically extract metadata

        Returns:
            Added PDFDocument instance
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Destination path in internal storage
        dest_filename = f"{file_path.stem}_{file_path.suffix}"
        dest_path = self.storage_path / dest_filename
        
        # If file already exists in storage, add a suffix
        counter = 1
        while dest_path.exists():
            dest_path = self.storage_path / f"{file_path.stem}_{counter}{file_path.suffix}"
            counter += 1

        # Copy file to internal storage
        shutil.copy2(file_path, dest_path)

        # Create model instance
        pdf = PDFDocument(
            title=file_path.name,
            file_path=str(dest_path)
        )

        if auto_extract:
            self.extract_metadata(pdf)

        self.session.add(pdf)
        self.session.commit()
        return pdf

    def extract_metadata(self, pdf: PDFDocument):
        """
        Extract metadata from a PDF file.

        Args:
            pdf: PDFDocument instance
        """
        try:
            with pdfplumber.open(pdf.file_path) as pipe:
                # Basic metadata from PDF info
                info = pipe.metadata
                if info.get("Title"):
                    pdf.title = info["Title"]
                if info.get("Author"):
                    pdf.authors = info["Author"]

                # Advanced extraction: Header for title/authors
                first_page = pipe.pages[0]
                text = first_page.extract_text()
                lines = text.split('\n') if text else []

                # Heuristic: If title is still filename, try first few lines
                if pdf.title == Path(pdf.file_path).name and lines:
                    pdf.title = lines[0].strip()[:200]

                # Heuristic: Find abstract
                self._extract_abstract(pipe, pdf)

        except Exception as e:
            logger.error(f"Error extracting metadata from {pdf.file_path}: {e}")

    def _extract_abstract(self, pipe, pdf: PDFDocument):
        """Internal helper to extract abstract."""
        keywords = self.config.get("extraction.pdf.abstract_keywords", ["abstract", "résumé"])
        max_pages = self.config.get("extraction.pdf.max_pages_for_abstract", 3)
        
        abstract_text = ""
        found = False

        for i in range(min(max_pages, len(pipe.pages))):
            text = pipe.pages[i].extract_text()
            if not text:
                continue

            lower_text = text.lower()
            for kw in keywords:
                if kw.lower() in lower_text:
                    # Find start of abstract
                    start_idx = lower_text.find(kw.lower())
                    # Take up to 2000 chars after the keyword
                    abstract_text = text[start_idx:].strip()
                    found = True
                    break
            if found:
                break
        
        if abstract_text:
            # Clean up: stop at next major section if possible
            # Simplified: just take first 1500 chars for now
            pdf.abstract = abstract_text[:2000]

    def get_pdf(self, pdf_id: int) -> Optional[PDFDocument]:
        """Get a PDF by ID."""
        return self.session.query(PDFDocument).filter(PDFDocument.id == pdf_id).first()

    def list_pdfs(self) -> List[PDFDocument]:
        """List all PDFs."""
        return self.session.query(PDFDocument).all()

    def delete_pdf(self, pdf_id: int, delete_file: bool = True):
        """Delete a PDF."""
        pdf = self.get_pdf(pdf_id)
        if pdf:
            if delete_file and Path(pdf.file_path).exists():
                try:
                    Path(pdf.file_path).unlink()
                except Exception as e:
                    logger.error(f"Failed to delete file {pdf.file_path}: {e}")
            self.session.delete(pdf)
            self.session.commit()
