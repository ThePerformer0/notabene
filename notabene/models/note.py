"""Note model."""
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from notabene.core.database import Base


class NoteType(enum.Enum):
    """Types of notes."""

    GENERAL = "general"
    IDEA = "idea"
    ARGUMENT = "argument"
    QUESTION = "question"
    QUOTE = "quote"


class Note(Base):
    """Model for notes attached to sources."""

    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    content = Column(Text, nullable=False)
    note_type = Column(
        Enum(NoteType), default=NoteType.GENERAL, nullable=False
    )
    date_created = Column(DateTime, default=datetime.utcnow, nullable=False)
    date_modified = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    source = relationship("Source", back_populates="notes")

    def __repr__(self) -> str:
        content_preview = (
            self.content[:50] + "..." if len(self.content) > 50 else self.content
        )
        return f"<Note(id={self.id}, source_id={self.source_id}, type={self.note_type.value}, content='{content_preview}')>"

    def to_dict(self) -> dict:
        """Convert note to dictionary."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "content": self.content,
            "note_type": self.note_type.value,
            "date_created": self.date_created.isoformat() if self.date_created else None,
            "date_modified": self.date_modified.isoformat()
            if self.date_modified
            else None,
        }
