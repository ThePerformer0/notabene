"""Integration tests for PDF ingestion in NotaBene.

Tests multi-page document parsing, coherence between eager and lazy extraction,
and streaming performance on larger documents.
"""

from pathlib import Path

import fitz
import pytest

from notabene.ingestion.pdf import extract_pdf, extract_pdf_pages_lazy


@pytest.fixture
def multipage_academic_pdf(tmp_path: Path) -> Path:
    """Create a realistic 10-page academic paper PDF fixture with varied content per page."""
    pdf_path = tmp_path / "academic_paper_10p.pdf"
    doc = fitz.open()

    sections = [
        ("1. Abstract", "This paper introduces a novel approach to local RAG pipelines."),
        ("2. Introduction", "Modern language models require grounded retrieval for high accuracy."),
        ("3. Related Work", "Previous studies explored vector index partitioning and dense passage retrieval."),
        ("4. System Architecture", "NotaBene adopts a modular pipeline separating ingestion, embedding, and storage."),
        ("5. Document Ingestion", "PyMuPDF enables streaming text extraction with minimal memory overhead."),
        ("6. Chunking Strategies", "Recursive semantic chunking preserves contextual boundaries between paragraphs."),
        ("7. Vector Indexing", "ChromaDB provides fast nearest neighbor search over local dense embeddings."),
        ("8. Experimental Setup", "We benchmarked precision, recall, and throughput on synthetic academic datasets."),
        ("9. Results & Discussion", "The local pipeline achieves sub-50ms latency without transmitting data off-device."),
        ("10. Conclusion & Future Work", "Future extensions include multi-modal figure extraction and agentic synthesis."),
    ]

    for title, body in sections:
        page = doc.new_page()
        page.insert_text((50, 72), f"{title}\n\n{body}\nPage index details and references.")

    doc.set_metadata(
        {
            "title": "NotaBene: Grounded Local Academic Research Assistant",
            "author": "NotaBene Research Team",
            "subject": "Computer Science - Information Retrieval",
        }
    )
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


@pytest.fixture
def large_50page_pdf(tmp_path: Path) -> Path:
    """Create a 50-page synthetic PDF document for streaming verification."""
    pdf_path = tmp_path / "large_document_50p.pdf"
    doc = fitz.open()

    for idx in range(1, 51):
        page = doc.new_page()
        page.insert_text(
            (50, 72),
            f"Volume {idx}: Statistical physics and computational mechanics section {idx}.\n"
            f"Detailed derivations for equation {idx * 7}.",
        )

    doc.set_metadata({"title": "Comprehensive Lecture Series (50 Volumes)"})
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


def test_e2e_multipage_pdf_eager_and_lazy_coherence(multipage_academic_pdf: Path) -> None:
    """Verify that extract_pdf and extract_pdf_pages_lazy return identical content on multi-page PDF."""
    # Eager extraction
    extracted = extract_pdf(multipage_academic_pdf)
    assert extracted.page_count == 10
    assert len(extracted.pages) == 10
    assert extracted.title == "NotaBene: Grounded Local Academic Research Assistant"
    assert extracted.author == "NotaBene Research Team"

    # Lazy streaming extraction
    lazy_pages = list(extract_pdf_pages_lazy(multipage_academic_pdf))
    assert len(lazy_pages) == 10

    # Verify 1-to-1 equivalence for each page
    for eager_p, lazy_p in zip(extracted.pages, lazy_pages):
        assert eager_p.number == lazy_p.number
        assert eager_p.text == lazy_p.text
        assert eager_p.char_count == lazy_p.char_count

    # Verify full concatenated text matches joined lazy pages
    lazy_full_text = "\n\n".join(p.text for p in lazy_pages)
    assert extracted.full_text == lazy_full_text


def test_lazy_streaming_partial_consumption(large_50page_pdf: Path) -> None:
    """Verify that extract_pdf_pages_lazy allows partial consumption without reading all 50 pages."""
    stream = extract_pdf_pages_lazy(large_50page_pdf)

    # Consume only first 2 pages
    p1 = next(stream)
    p2 = next(stream)

    assert p1.number == 1
    assert "Volume 1" in p1.text

    assert p2.number == 2
    assert "Volume 2" in p2.text

    # Closing generator prematurely should not raise any error
    stream.close()
