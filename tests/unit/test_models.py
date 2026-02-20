import pytest
from datetime import datetime
from notabene.models.base import Source
from notabene.models.pdf import PDFDocument
from notabene.models.web import WebSource
from notabene.models.note import Note, NoteType
from notabene.models.tag import Tag

def test_source_creation(db_session):
    """Test creating a generic source."""
    source = Source(title="Test Source", type="source")
    db_session.add(source)
    db_session.commit()
    
    saved_source = db_session.query(Source).filter_by(title="Test Source").first()
    assert saved_source is not None
    assert saved_source.id is not None
    assert saved_source.type == "source"

def test_pdf_document_creation(db_session):
    """Test creating a PDF document with specific fields."""
    pdf = PDFDocument(
        title="Attention is All You Need",
        authors="Vaswani et al.",
        year="2017",
        journal="NIPS",
        file_path="/path/to/attention.pdf",
        type="pdf"
    )
    db_session.add(pdf)
    db_session.commit()
    
    saved_pdf = db_session.query(PDFDocument).filter_by(year="2017").first()
    assert saved_pdf.title == "Attention is All You Need"
    assert saved_pdf.authors == "Vaswani et al."
    assert saved_pdf.type == "pdf"

def test_web_source_creation(db_session):
    """Test creating a Web source."""
    web = WebSource(
        title="Python.org",
        url="https://www.python.org",
        domain="www.python.org",
        date_published=datetime(2023, 1, 1),
        type="web"
    )
    db_session.add(web)
    db_session.commit()
    
    saved_web = db_session.query(WebSource).filter_by(domain="www.python.org").first()
    assert saved_web.url == "https://www.python.org"
    assert saved_web.date_published is not None

def test_note_relationship(db_session):
    """Test attaching notes to a source."""
    source = Source(title="Note Source", type="source")
    db_session.add(source)
    db_session.commit()
    
    note = Note(
        source_id=source.id,
        content="Interesting fact",
        note_type=NoteType.IDEA
    )
    db_session.add(note)
    db_session.commit()
    
    # Reload source to check relationship
    reloaded_source = db_session.query(Source).get(source.id)
    assert len(reloaded_source.notes) == 1
    assert reloaded_source.notes[0].content == "Interesting fact"
    assert reloaded_source.notes[0].note_type == NoteType.IDEA

def test_tag_relationship(db_session):
    """Test tagging a source."""
    source = Source(title="Tagged Source", type="source")
    tag = Tag(name="research")
    source.tags.append(tag)
    
    db_session.add(source)
    db_session.commit()
    
    reloaded_source = db_session.query(Source).filter_by(title="Tagged Source").first()
    assert len(reloaded_source.tags) == 1
    assert reloaded_source.tags[0].name == "research"
    
    reloaded_tag = db_session.query(Tag).filter_by(name="research").first()
    assert len(reloaded_tag.sources) == 1
    assert reloaded_tag.sources[0].title == "Tagged Source"
