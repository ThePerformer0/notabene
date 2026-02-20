import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from notabene.utils import pdf_extractor, web_extractor, bibtex_exporter, markdown_exporter
from notabene.models.pdf import PDFDocument
from notabene.models.web import WebSource

def test_pdf_extractor_logic(tmp_path):
    """Test PDF extraction logic with mocks."""
    dummy_pdf = tmp_path / "test.pdf"
    dummy_pdf.write_text("test")
    
    with patch("pdfplumber.open") as mock_open:
        mock_open.return_value.__enter__.return_value.metadata = {"Title": "Extracted Title", "Author": "Extracted Author"}
        mock_open.return_value.__enter__.return_value.pages = [MagicMock()]
        
        meta = pdf_extractor.extract_metadata(str(dummy_pdf))
        assert meta["title"] == "Extracted Title"
        assert meta["authors"] == "Extracted Author"

def test_web_extractor_logic():
    """Test Web extraction logic with mocks."""
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b"<html><title>Page Title</title></html>"
        
        meta = web_extractor.extract_metadata("https://test.com")
        assert meta["title"] == "Page Title"

def test_exporters(tmp_path):
    """Test BibTeX and Markdown exporters output format."""
    bib_file = tmp_path / "test.bib"
    md_file = tmp_path / "test.md"
    
    pdf = PDFDocument(id=1, title="Paper", authors="Author", year="2020", type="pdf")
    sources = [pdf]
    
    # BibTeX
    bibtex_exporter.export_to_bibtex(sources, str(bib_file))
    content = bib_file.read_text()
    assert "@article{Author2020Paper_1" in content
    assert "title = {Paper}" in content
    
    # Markdown
    markdown_exporter.export_to_markdown(sources, str(md_file))
    content = md_file.read_text()
    assert "# Exported Notes" in content
    assert "## Paper" in content
