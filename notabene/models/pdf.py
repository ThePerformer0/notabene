"""PDF document model."""
from sqlalchemy import Column, String, Text

from notabene.models.base import Source


class PDFDocument(Source):
    """Model for PDF documents."""

    __mapper_args__ = {
        "polymorphic_identity": "pdf",
    }

    # PDF-specific fields (nullable for single-table inheritance)
    file_path = Column(String(1000), unique=True)
    abstract = Column(Text)
    doi = Column(String(200))
    journal = Column(String(300))
    year = Column(String(4))
    keywords = Column(Text)  # Comma-separated keywords

    def __repr__(self) -> str:
        return f"<PDFDocument(id={self.id}, title='{self.title}', file='{self.file_path}')>"

    def to_dict(self) -> dict:
        """Convert PDF document to dictionary."""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "file_path": self.file_path,
                "abstract": self.abstract,
                "doi": self.doi,
                "journal": self.journal,
                "year": self.year,
                "keywords": self.keywords,
            }
        )
        return base_dict
