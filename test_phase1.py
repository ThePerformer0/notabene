"""Test script to verify Phase 1 implementation."""
from pathlib import Path
import tempfile

from notabene.core.config import init_config
from notabene.core.database import init_database, get_database
from notabene.models import (
    PDFDocument,
    WebSource,
    Note,
    NoteType,
    Tag,
    Link,
    LinkType,
)


def test_phase1():
    """Test Phase 1: Database and Models."""
    print("=== Testing Phase 1: Database and Models ===\n")

    # Create temporary database
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"

        # Initialize config and database
        print("[1] Initializing configuration...")
        config = init_config()
        print(f"    OK - Config loaded: DB path = {config.db_path}")

        print("\n[2] Initializing database...")
        db = init_database(db_path)
        print(f"    OK - Database created at {db_path}")

        # Test session
        print("\n[3] Testing database session...")
        session_gen = db.get_session()
        session = next(session_gen)
        print("    OK - Session created")

        # Create a PDF document
        print("\n[4] Creating PDF document...")
        pdf = PDFDocument(
            title="Machine Learning: A Probabilistic Perspective",
            authors="Kevin P. Murphy",
            file_path="/path/to/ml_book.pdf",
            abstract="This textbook offers a comprehensive introduction to machine learning.",
            year="2012",
            journal="MIT Press",
        )
        session.add(pdf)
        session.commit()
        print(f"    OK - PDF created: {pdf}")

        # Create a web source
        print("\n[5] Creating web source...")
        web = WebSource(
            title="Python Documentation",
            authors="Python Software Foundation",
            url="https://docs.python.org/3/",
            domain="docs.python.org",
        )
        session.add(web)
        session.commit()
        print(f"    OK - Web source created: {web}")

        # Create notes
        print("\n[6] Creating notes...")
        note1 = Note(
            source_id=pdf.id,
            content="Great introduction to probabilistic models",
            note_type=NoteType.IDEA,
        )
        note2 = Note(
            source_id=web.id,
            content="Check the asyncio documentation",
            note_type=NoteType.QUESTION,
        )
        session.add_all([note1, note2])
        session.commit()
        print(f"    OK - Created {2} notes")

        # Create tags
        print("\n[7] Creating tags...")
        tag_ml = Tag(name="machine-learning", description="ML related sources")
        tag_python = Tag(name="python", description="Python programming")
        session.add_all([tag_ml, tag_python])
        session.commit()

        # Associate tags with sources
        pdf.tags.append(tag_ml)
        web.tags.append(tag_python)
        session.commit()
        print(f"    OK - Created and associated tags")

        # Create link
        print("\n[8] Creating link between sources...")
        link = Link(
            source_from_id=pdf.id,
            source_to_id=web.id,
            link_type=LinkType.RELATED,
            description="Both useful for ML in Python",
        )
        session.add(link)
        session.commit()
        print(f"    OK - Link created: {link}")

        # Query and display
        print("\n[9] Querying database...")
        all_sources = session.query(PDFDocument).all() + session.query(WebSource).all()
        print(f"    OK - Found {len(all_sources)} sources:")
        for source in all_sources:
            print(f"       - {source.type.upper()}: {source.title}")
            print(f"         Tags: {[tag.name for tag in source.tags]}")
            print(f"         Notes: {len(source.notes)}")

        # Test to_dict methods
        print("\n[10] Testing to_dict() methods...")
        print(f"     PDF dict: {pdf.to_dict()}")
        print(f"     Web dict: {web.to_dict()}")
        print(f"     Note dict: {note1.to_dict()}")
        print(f"     Tag dict: {tag_ml.to_dict()}")
        print(f"     Link dict: {link.to_dict()}")

        # Properly close session and dispose engine
        session.close()
        db.engine.dispose()  # Important for Windows to release file lock

    print("\n" + "="*50)
    print("SUCCESS - Phase 1 test completed!")
    print("="*50)
    print("\nSummary:")
    print("  [OK] Database configuration")
    print("  [OK] Models (Source, PDF, Web)")
    print("  [OK] Notes with types")
    print("  [OK] Tags with many-to-many")
    print("  [OK] Links between sources")
    print("  [OK] Relationships working")


if __name__ == "__main__":
    test_phase1()
