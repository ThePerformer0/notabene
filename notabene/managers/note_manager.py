"""Management of notes."""
from typing import List, Optional
from sqlalchemy.orm import Session

from notabene.models.note import Note, NoteType


class NoteManager:
    """Manager for notes."""

    def __init__(self, session: Session):
        """
        Initialize the manager.

        Args:
            session: Database session
        """
        self.session = session

    def add_note(self, source_id: int, content: str, note_type: NoteType = NoteType.GENERAL) -> Note:
        """
        Add a note to a source.

        Args:
            source_id: ID of the source
            content: Content of the note
            note_type: Type of the note

        Returns:
            Added Note instance
        """
        note = Note(
            source_id=source_id,
            content=content,
            note_type=note_type
        )
        self.session.add(note)
        self.session.commit()
        return note

    def get_notes(self, source_id: int) -> List[Note]:
        """Get all notes for a source."""
        return self.session.query(Note).filter(Note.source_id == source_id).all()

    def update_note(self, note_id: int, content: Optional[str] = None, note_type: Optional[NoteType] = None) -> Optional[Note]:
        """Update a note."""
        note = self.session.query(Note).filter(Note.id == note_id).first()
        if note:
            if content is not None:
                note.content = content
            if note_type is not None:
                note.note_type = note_type
            self.session.commit()
        return note

    def delete_note(self, note_id: int):
        """Delete a note."""
        note = self.session.query(Note).filter(Note.id == note_id).first()
        if note:
            self.session.delete(note)
            self.session.commit()
