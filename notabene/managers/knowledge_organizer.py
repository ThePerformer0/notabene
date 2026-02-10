"""Organization of knowledge through tags and links."""
from typing import List, Optional
from sqlalchemy.orm import Session

from notabene.models.base import Source
from notabene.models.tag import Tag
from notabene.models.link import Link, LinkType


class KnowledgeOrganizer:
    """Manager for tags and links."""

    def __init__(self, session: Session):
        """
        Initialize the manager.

        Args:
            session: Database session
        """
        self.session = session

    # Tag management
    def add_tag(self, source_id: int, tag_name: str) -> Tag:
        """Add a tag to a source."""
        source = self.session.query(Source).filter(Source.id == source_id).first()
        if not source:
            raise ValueError(f"Source not found: {source_id}")

        tag = self.session.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            self.session.add(tag)
        
        if tag not in source.tags:
            source.tags.append(tag)
        
        self.session.commit()
        return tag

    def remove_tag(self, source_id: int, tag_name: str):
        """Remove a tag from a source."""
        source = self.session.query(Source).filter(Source.id == source_id).first()
        if source:
            source.tags = [t for t in source.tags if t.name != tag_name]
            self.session.commit()

    def get_sources_by_tag(self, tag_name: str) -> List[Source]:
        """Get all sources associated with a tag."""
        tag = self.session.query(Tag).filter(Tag.name == tag_name).first()
        return tag.sources if tag else []

    # Link management
    def link_sources(self, source_from_id: int, source_to_id: int, 
                     link_type: LinkType = LinkType.RELATED, 
                     description: str = "") -> Link:
        """Link two sources together."""
        link = Link(
            source_from_id=source_from_id,
            source_to_id=source_to_id,
            link_type=link_type,
            description=description
        )
        self.session.add(link)
        self.session.commit()
        return link

    def get_related_sources(self, source_id: int) -> List[Source]:
        """Get all sources linked to or from a source."""
        source = self.session.query(Source).filter(Source.id == source_id).first()
        if not source:
            return []
        
        related = set()
        for link in source.links_from:
            related.add(link.source_to)
        for link in source.links_to:
            related.add(link.source_from)
        
        return list(related)
