"""Base model for all sources."""
from datetime import datetime
from typing import List

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship

from notabene.core.database import Base


class Source(Base):
    """
    Base model for all sources (PDF and Web).

    This is an abstract base class using SQLAlchemy's single table inheritance.
    """

    __tablename__ = "sources"

    # Polymorphic configuration
    __mapper_args__ = {
        "polymorphic_identity": "source",
        "polymorphic_on": "type",
    }

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Polymorphic discriminator
    type = Column(String(50), nullable=False)

    # Common fields
    title = Column(String(500), nullable=False)
    authors = Column(String(500))  # Comma-separated list
    date_added = Column(DateTime, default=datetime.utcnow, nullable=False)
    date_modified = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    notes = relationship(
        "Note", back_populates="source", cascade="all, delete-orphan"
    )
    tags = relationship(
        "Tag", secondary="source_tags", back_populates="sources"
    )
    links_from = relationship(
        "Link",
        foreign_keys="Link.source_from_id",
        back_populates="source_from",
        cascade="all, delete-orphan",
    )
    links_to = relationship(
        "Link",
        foreign_keys="Link.source_to_id",
        back_populates="source_to",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Source(id={self.id}, type={self.type}, title='{self.title}')>"

    def to_dict(self) -> dict:
        """Convert source to dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "authors": self.authors,
            "date_added": self.date_added.isoformat() if self.date_added else None,
            "date_modified": self.date_modified.isoformat()
            if self.date_modified
            else None,
        }
