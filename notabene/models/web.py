"""Web source model."""
from datetime import datetime

from sqlalchemy import Column, String, DateTime

from notabene.models.base import Source


class WebSource(Source):
    """Model for web sources."""

    __mapper_args__ = {
        "polymorphic_identity": "web",
    }

    # Web-specific fields (nullable for single-table inheritance)
    url = Column(String(2000), unique=True)
    domain = Column(String(200))
    date_published = Column(DateTime)
    date_accessed = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<WebSource(id={self.id}, title='{self.title}', url='{self.url}')>"

    def to_dict(self) -> dict:
        """Convert web source to dictionary."""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "url": self.url,
                "domain": self.domain,
                "date_published": self.date_published.isoformat()
                if self.date_published
                else None,
                "date_accessed": self.date_accessed.isoformat()
                if self.date_accessed
                else None,
            }
        )
        return base_dict
