"""Link model for relationships between sources."""
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from notabene.core.database import Base


class LinkType(enum.Enum):
    """Types of relationships between sources."""

    CITES = "cites"  # Source A cites Source B
    CITED_BY = "cited_by"  # Source A is cited by Source B
    RELATED = "related"  # General relation
    CONTRADICTS = "contradicts"  # Source A contradicts Source B
    SUPPORTS = "supports"  # Source A supports Source B
    EXTENDS = "extends"  # Source A extends Source B


class Link(Base):
    """Model for links between sources."""

    __tablename__ = "links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_from_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    source_to_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    link_type = Column(Enum(LinkType), default=LinkType.RELATED, nullable=False)
    description = Column(String(500))
    date_created = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    source_from = relationship(
        "Source", foreign_keys=[source_from_id], back_populates="links_from"
    )
    source_to = relationship(
        "Source", foreign_keys=[source_to_id], back_populates="links_to"
    )

    def __repr__(self) -> str:
        return f"<Link(id={self.id}, from={self.source_from_id}, to={self.source_to_id}, type={self.link_type.value})>"

    def to_dict(self) -> dict:
        """Convert link to dictionary."""
        return {
            "id": self.id,
            "source_from_id": self.source_from_id,
            "source_to_id": self.source_to_id,
            "link_type": self.link_type.value,
            "description": self.description,
            "date_created": self.date_created.isoformat() if self.date_created else None,
        }
