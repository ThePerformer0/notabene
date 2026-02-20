import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from notabene.managers.document_manager import DocumentManager
from notabene.managers.web_source_manager import WebSourceManager
from notabene.managers.note_manager import NoteManager
from notabene.managers.knowledge_organizer import KnowledgeOrganizer
from notabene.models.note import NoteType

@pytest.fixture
def doc_manager(db_session, temp_storage):
    """Fixture for DocumentManager with temp storage."""
    with patch("notabene.managers.document_manager.get_config") as mock_config:
        cfg = MagicMock()
        cfg.pdf_directory = temp_storage
        # Mock the get method to return real defaults
        def mock_get(key, default=None):
            if key == "storage.pdf_directory": return str(temp_storage)
            if key == "extraction.pdf.abstract_keywords": return ["abstract", "résumé"]
            if key == "extraction.pdf.max_pages_for_abstract": return 3
            return default
        cfg.get.side_effect = mock_get
        mock_config.return_value = cfg
        manager = DocumentManager(db_session)
        return manager

def test_add_pdf(doc_manager, temp_storage):
    """Test adding a PDF (mocking pdfplumber and shutil)."""
    # Create a dummy pdf file
    dummy_pdf = temp_storage / "test.pdf"
    dummy_pdf.write_text("dummy content")
    
    with patch("shutil.copy2"), \
         patch("pdfplumber.open") as mock_pdf:
        
        # Mock pdfplumber behavior
        mock_pdf.return_value.__enter__.return_value.metadata = {"Title": "Mock Title", "Author": "Mock Author"}
        mock_pdf.return_value.__enter__.return_value.pages = [MagicMock()]
        mock_pdf.return_value.__enter__.return_value.pages[0].extract_text.return_value = "Abstract: This is a test."
        
        doc = doc_manager.add_pdf(dummy_pdf)
        
        assert doc.id is not None
        assert doc.title == "Mock Title"
        assert doc.authors == "Mock Author"
        assert "Abstract: This is a test." in doc.abstract

def test_add_web_source(db_session):
    """Test adding a web source (mocking requests)."""
    with patch("requests.get") as mock_get:
        # Mock response
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "<html><title>Python Home</title></html>"
        mock_get.return_value = mock_resp
        
        manager = WebSourceManager(db_session)
        web = manager.add_web_source("https://www.python.org")
        
        assert web.title == "Python Home"
        assert web.domain == "www.python.org"

def test_note_manager(db_session):
    """Test note operations."""
    from notabene.models.base import Source
    source = Source(title="Note Test", type="source")
    db_session.add(source)
    db_session.commit()
    
    manager = NoteManager(db_session)
    note = manager.add_note(source.id, "Testing notes", NoteType.QUESTION)
    
    assert note.id is not None
    assert note.content == "Testing notes"
    
    notes = manager.get_notes(source.id)
    assert len(notes) == 1

def test_knowledge_organizer(db_session):
    """Test tagging and linking."""
    from notabene.models.base import Source
    s1 = Source(title="S1", type="source")
    db_session.add(s1)
    db_session.commit()
    
    manager = KnowledgeOrganizer(db_session)
    manager.add_tag(s1.id, "tag1")
    
    reloaded = db_session.query(Source).get(s1.id)
    assert reloaded.tags[0].name == "tag1"
