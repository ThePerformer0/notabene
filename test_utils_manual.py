import sys
import os
from datetime import datetime

# Add the project root to the python path
sys.path.append(os.getcwd())

from notabene.utils import pdf_extractor, web_extractor, bibtex_exporter, markdown_exporter
from notabene.models.pdf import PDFDocument
from notabene.models.web import WebSource
from notabene.models.note import Note, NoteType

def test_extractors():
    print("\n--- Testing Extractors ---")
    
    # Test Web Extractor
    url = "https://www.python.org"
    print(f"Testing Web Extractor on {url}...")
    web_meta = web_extractor.extract_metadata(url)
    print(f"Extracted Web Metadata: {web_meta}")

    # Test PDF Extractor (Placeholder as we don't have a guaranteed PDF)
    # create a dummy empty file to test file existence check
    with open("dummy.pdf", "w") as f:
        f.write("test")
    
    try:
        print(f"Testing PDF Extractor on dummy.pdf (should fail parsing but run)...")
        pdf_meta = pdf_extractor.extract_metadata("dummy.pdf")
        print(f"Extracted PDF Metadata: {pdf_meta}")
    except Exception as e:
        print(f"Caught expected exception for dummy pdf: {e}")
    finally:
        if os.path.exists("dummy.pdf"):
            os.remove("dummy.pdf")

def test_exporters():
    print("\n--- Testing Exporters ---")

    # Create dummy sources
    pdf_source = PDFDocument(
        id=1,
        title="Attention Is All You Need",
        authors="Vaswani et al.",
        year="2017",
        journal="NIPS",
        date_added=datetime.now(),
        type="pdf"
    )
    
    web_source = WebSource(
        id=2,
        title="Python Official Site",
        url="https://python.org",
        date_accessed=datetime.now(),
        date_published=datetime(2023, 10, 24),
        type="web"
    )

    # Add notes
    note1 = Note(
        id=1,
        source_id=1,
        content="This is a groundbreaking paper on Transformers.",
        note_type=NoteType.IDEA,
        date_created=datetime.now()
    )
    pdf_source.notes = [note1]

    sources = [pdf_source, web_source]

    # Test BibTeX Export
    bibtex_file = "test_export.bib"
    print(f"Exporting to {bibtex_file}...")
    bibtex_exporter.export_to_bibtex(sources, bibtex_file)
    with open(bibtex_file, "r") as f:
        print("BibTeX Content:")
        print(f.read())
    
    # Test Markdown Export
    markdown_file = "test_export.md"
    print(f"Exporting to {markdown_file}...")
    markdown_exporter.export_to_markdown(sources, markdown_file)
    with open(markdown_file, "r") as f:
        print("Markdown Content:")
        print(f.read())

    # Cleanup
    if os.path.exists(bibtex_file):
        os.remove(bibtex_file)
    if os.path.exists(markdown_file):
        os.remove(markdown_file)

if __name__ == "__main__":
    test_extractors()
    test_exporters()
