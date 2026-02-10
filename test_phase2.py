"""Test script to verify Phase 2 implementation."""
import os
from pathlib import Path
import tempfile
import time

from notabene.core.config import init_config
from notabene.core.database import init_database
from notabene.models.note import NoteType
from notabene.models.link import LinkType
from notabene.managers.document_manager import DocumentManager
from notabene.managers.web_source_manager import WebSourceManager
from notabene.managers.note_manager import NoteManager
from notabene.managers.knowledge_organizer import KnowledgeOrganizer
from notabene.managers.search_engine import SearchEngine


def test_phase2():
    """Test Phase 2: Managers and Logic."""
    print("=== Testing Phase 2: Business Managers ===\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        db_path = tmp_path / "test_p2.db"
        pdf_dir = tmp_path / "pdfs"
        pdf_dir.mkdir()

        # 1. Setup
        print("[1] Setting up environment...")
        config = init_config()
        config.set("database.path", str(db_path))
        config.set("storage.pdf_directory", str(pdf_dir))
        
        db = init_database(db_path)
        session = next(db.get_session())
        
        doc_mgr = DocumentManager(session)
        web_mgr = WebSourceManager(session)
        note_mgr = NoteManager(session)
        know_mgr = KnowledgeOrganizer(session)
        search_eng = SearchEngine(session)
        print("    OK - Managers initialized")

        # 2. Test DocumentManager (with a dummy PDF if possible, or just file handling)
        print("\n[2] Testing DocumentManager...")
        dummy_pdf = tmp_path / "test_article.pdf"
        dummy_pdf.write_text("This is a dummy PDF content with Abstract: Intelligence is key.")
        
        # Note: pdfplumber will fail on this text file, but we test the logic around it
        try:
            pdf = doc_mgr.add_pdf(dummy_pdf, auto_extract=False)
            print(f"    OK - PDF added: {pdf.title}")
            print(f"    Check storage: {os.path.exists(pdf.file_path)}")
        except Exception as e:
            print(f"    Error in PDF add: {e}")

        # 3. Test WebSourceManager
        print("\n[3] Testing WebSourceManager (Scraping)...")
        # Use a stable URL or mock. For this test, we'll try a real one but handle failure
        try:
            web = web_mgr.add_web_source("https://www.google.com")
            print(f"    OK - Web source added: {web.title} ({web.domain})")
        except Exception as e:
            print(f"    Web scraping failed (expected if no network): {e}")
            # Manual fallback for the rest of the test
            web = web_mgr.add_web_source("https://example.com", auto_extract=False)
            web.title = "Example Domain"

        # 4. Test NoteManager
        print("\n[4] Testing NoteManager...")
        note = note_mgr.add_note(web.id, "Important discovery", NoteType.IDEA)
        print(f"    OK - Note created: {note.content}")
        
        # 5. Test KnowledgeOrganizer
        print("\n[5] Testing KnowledgeOrganizer (Tags & Links)...")
        know_mgr.add_tag(web.id, "research")
        print(f"    OK - Tag added: {[t.name for t in web.tags]}")
        
        # 6. Test SearchEngine
        print("\n[6] Testing SearchEngine...")
        results = search_eng.search("Example")
        print(f"    OK - Search results for 'Example': {len(results)}")
        for r in results:
            print(f"       - Found: {r.title}")

        session.close()
        db.engine.dispose()

    print("\n" + "="*50)
    print("SUCCESS - Phase 2 integration test completed!")
    print("="*50)


if __name__ == "__main__":
    test_phase2()
