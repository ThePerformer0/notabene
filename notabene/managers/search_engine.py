"""Search engine for research sources."""
from typing import List
from sqlalchemy import or_
from sqlalchemy.orm import Session

from notabene.models.base import Source
from notabene.models.pdf import PDFDocument
from notabene.models.web import WebSource
from notabene.models.tag import Tag


class SearchEngine:
    """Search engine for sources, tags, and notes."""

    def __init__(self, session: Session):
        """
        Initialize the manager.

        Args:
            session: Database session
        """
        self.session = session

    def search(self, query: str) -> List[Source]:
        """
        Search sources by keyword in title, authors, or abstract.

        Args:
            query: Search query string

        Returns:
            List of matching Source instances
        """
        q = f"%{query}%"
        
        # Search in Source (Title, Authors)
        results = self.session.query(Source).filter(
            or_(
                Source.title.ilike(q),
                Source.authors.ilike(q)
            )
        ).all()
        
        # Search in PDF specifically (Abstract, Keywords)
        pdf_results = self.session.query(PDFDocument).filter(
            or_(
                PDFDocument.abstract.ilike(q),
                PDFDocument.keywords.ilike(q)
            )
        ).all()
        
        # Combine and deduplicate
        combined = {s.id: s for s in results}
        for s in pdf_results:
            combined[s.id] = s
            
        return list(combined.values())

    def search_by_tag(self, tag_name: str) -> List[Source]:
        """Search sources by tag name."""
        tag = self.session.query(Tag).filter(Tag.name.ilike(tag_name)).first()
        return tag.sources if tag else []

    def search_by_author(self, author_name: str) -> List[Source]:
        """Search sources by author name."""
        q = f"%{author_name}%"
        return self.session.query(Source).filter(Source.authors.ilike(q)).all()
