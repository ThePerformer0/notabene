"""Integration tests for web page ingestion in NotaBene.

Tests the full extraction pipeline end-to-end on simulated multi-paragraph
academic articles with rich metadata, verifying content integrity,
metadata normalization, and hash determinism.
"""

from datetime import timezone
import json

import pytest
import trafilatura

from notabene.ingestion.web import ExtractedWebPage, extract_web_page


@pytest.fixture
def mock_academic_web_article(monkeypatch: pytest.MonkeyPatch) -> str:
    """Fixture providing simulated fetch and extract responses for an academic article."""
    target_url = "https://openreview.net/forum?id=kXZ982L"
    simulated_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Dense Passage Retrieval for Academic RAG</title>
        <meta name="author" content="Dr. Marie Curie; Prof. Alan Turing">
        <meta property="og:site_name" content="OpenReview">
        <meta name="date" content="2026-03-15">
    </head>
    <body>
        <article>
            <h1>Dense Passage Retrieval for Academic RAG</h1>
            <p>Open-domain question answering relies heavily on efficient passage retrieval.</p>
            <p>We demonstrate that dense embeddings outperform classical TF-IDF methods on scientific benchmarks.</p>
            <p>Our approach integrates multi-vector indexing with localized in-memory stores for extreme low latency.</p>
        </article>
    </body>
    </html>
    """

    simulated_json_payload = json.dumps(
        {
            "title": "Dense Passage Retrieval for Academic RAG",
            "author": "Dr. Marie Curie; Prof. Alan Turing",
            "sitename": "OpenReview",
            "date": "2026-03-15",
            "text": (
                "Open-domain question answering relies heavily on efficient passage retrieval.\n\n"
                "We demonstrate that dense embeddings outperform classical TF-IDF methods on scientific benchmarks.\n\n"
                "Our approach integrates multi-vector indexing with localized in-memory stores for extreme low latency."
            ),
        }
    )

    monkeypatch.setattr(trafilatura, "fetch_url", lambda *args, **kwargs: simulated_html)
    monkeypatch.setattr(trafilatura, "extract", lambda *args, **kwargs: simulated_json_payload)

    return target_url


def test_e2e_web_article_extraction(mock_academic_web_article: str) -> None:
    """Verify end-to-end web article extraction with full metadata and body parsing."""
    url = mock_academic_web_article
    extracted = extract_web_page(url, timeout=12.0)

    assert isinstance(extracted, ExtractedWebPage)
    assert extracted.url == url
    assert extracted.title == "Dense Passage Retrieval for Academic RAG"
    assert extracted.author == "Dr. Marie Curie; Prof. Alan Turing"
    assert extracted.site_name == "OpenReview"
    assert extracted.publish_date == "2026-03-15"

    assert "Open-domain question answering" in extracted.text
    assert "extreme low latency" in extracted.text
    assert len(extracted.content_hash) == 64
    assert extracted.extracted_at.tzinfo == timezone.utc


def test_e2e_web_article_content_hash_stability(mock_academic_web_article: str) -> None:
    """Verify that repeated extractions of the identical article yield an identical content hash."""
    url = mock_academic_web_article
    extracted_run1 = extract_web_page(url)
    extracted_run2 = extract_web_page(url)

    assert extracted_run1.content_hash == extracted_run2.content_hash
    assert extracted_run1.text == extracted_run2.text
