"""Tag model."""
from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship

from notabene.core.database import Base

# Association table for many-to-many relationship between sources and tags
source_tags = Table(
    "source_tags",
    Base.metadata,
    Column("source_id", Integer, ForeignKey("sources.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class Tag(Base):
    """Model for tags to categorize sources."""

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(500))

    # Relationships
    sources = relationship(
        "Source", secondary=source_tags, back_populates="tags"
    )

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name='{self.name}')>"

    def to_dict(self) -> dict:
        """Convert tag to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "source_count": len(self.sources) if self.sources else 0,
        }
