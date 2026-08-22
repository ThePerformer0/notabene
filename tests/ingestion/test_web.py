"""Unit tests for notabene.ingestion.web module.

All network calls to trafilatura and requests are fully mocked to ensure
fast, deterministic, and isolated unit testing with zero external I/O.
"""

from datetime import timezone
import json
from unittest.mock import MagicMock

import pytest
import requests
import trafilatura

from notabene.ingestion.exceptions import (
    InvalidURLError,
    WebEmptyContentError,
    WebFetchError,
)
import notabene.ingestion.web as web_module
from notabene.ingestion.web import (
    ExtractedWebPage,
    _validate_url,
    compute_content_hash,
    extract_web_page,
)


def test_extract_web_page_valid_returns_correct_data(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that a valid HTML page with rich metadata is properly parsed and extracted."""
    fake_url = "https://arxiv.org/abs/2301.00000"
    fake_html = "<html><body><h1>Attention Is All You Need</h1><p>Main text content.</p></body></html>"
    fake_json_result = json.dumps(
        {
            "title": "Attention Is All You Need",
            "author": "Ashish Vaswani et al.",
            "sitename": "arXiv.org",
            "date": "2023-01-01",
            "text": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks.",
        }
    )

    mock_fetch = MagicMock(return_value=fake_html)
    mock_extract = MagicMock(return_value=fake_json_result)

    monkeypatch.setattr(trafilatura, "fetch_url", mock_fetch)
    monkeypatch.setattr(trafilatura, "extract", mock_extract)

    result = extract_web_page(fake_url, timeout=10.0)

    assert isinstance(result, ExtractedWebPage)
    assert result.url == fake_url
    assert result.title == "Attention Is All You Need"
    assert result.author == "Ashish Vaswani et al."
    assert result.site_name == "arXiv.org"
    assert result.publish_date == "2023-01-01"
    assert "The dominant sequence transduction models" in result.text
    assert len(result.content_hash) == 64
    assert result.extracted_at.tzinfo == timezone.utc

    mock_fetch.assert_called_once()
    mock_extract.assert_called_once()


def test_extract_web_page_missing_metadata_returns_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that missing metadata fields cleanly default to None without failing."""
    fake_url = "https://example.org/plain-post"
    fake_html = "<html><body><p>Just some plain text without header metadata.</p></body></html>"
    fake_json_result = json.dumps(
        {
            "title": None,
            "author": "",
            "sitename": None,
            "date": "   ",
            "text": "Just some plain text without header metadata.",
        }
    )

    monkeypatch.setattr(trafilatura, "fetch_url", lambda *args, **kwargs: fake_html)
    monkeypatch.setattr(trafilatura, "extract", lambda *args, **kwargs: fake_json_result)

    result = extract_web_page(fake_url)

    assert result.title is None
    assert result.author is None
    assert result.site_name is None
    assert result.publish_date is None
    assert result.text == "Just some plain text without header metadata."


@pytest.mark.parametrize(
    "invalid_url",
    [
        "example.com",
        "ftp://example.com/file.txt",
        "file:///path/to/file",
        "http://",
        "https://",
        "",
        "   ",
        "gopher://old.protocol.org",
    ],
)
def test_extract_web_page_invalid_url_raises(
    invalid_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that malformed or non-http(s) URLs raise InvalidURLError before any network call."""
    mock_fetch = MagicMock()
    monkeypatch.setattr(trafilatura, "fetch_url", mock_fetch)

    with pytest.raises(InvalidURLError) as exc_info:
        extract_web_page(invalid_url)

    assert exc_info.value.url == invalid_url
    mock_fetch.assert_not_called()


def test_extract_web_page_fetch_timeout_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that request timeout during fetch raises WebFetchError."""
    target_url = "https://slow-responsive-server.org/timeout"

    def mock_fetch_timeout(*args: object, **kwargs: object) -> None:
        raise requests.exceptions.Timeout("Connection timed out after 15s")

    monkeypatch.setattr(trafilatura, "fetch_url", mock_fetch_timeout)

    with pytest.raises(WebFetchError) as exc_info:
        extract_web_page(target_url)

    assert target_url in str(exc_info.value)
    assert exc_info.value.url == target_url
    assert isinstance(exc_info.value.cause, requests.exceptions.Timeout)


def test_extract_web_page_connection_error_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that network connection drops or DNS failures raise WebFetchError."""
    target_url = "https://nonexistent-domain-12345.org/article"

    def mock_fetch_conn_error(*args: object, **kwargs: object) -> None:
        raise requests.exceptions.ConnectionError("Failed to establish a new connection")

    monkeypatch.setattr(trafilatura, "fetch_url", mock_fetch_conn_error)

    with pytest.raises(WebFetchError) as exc_info:
        extract_web_page(target_url)

    assert target_url in str(exc_info.value)
    assert exc_info.value.url == target_url
    assert isinstance(exc_info.value.cause, requests.exceptions.ConnectionError)


def test_extract_web_page_fetch_returns_none_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that a silent failure in fetch_url (returning None) raises WebFetchError."""
    target_url = "https://httpstat.us/500"

    monkeypatch.setattr(trafilatura, "fetch_url", lambda *args, **kwargs: None)

    with pytest.raises(WebFetchError) as exc_info:
        extract_web_page(target_url)

    assert target_url in str(exc_info.value)
    assert exc_info.value.url == target_url


def test_extract_web_page_oversized_content_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that content exceeding the max size limit raises WebFetchError."""
    monkeypatch.setattr(web_module, "_MAX_CONTENT_SIZE_BYTES", 100)

    oversized_html = "<html><body>" + ("x" * 500) + "</body></html>"
    mock_extract = MagicMock()

    monkeypatch.setattr(trafilatura, "fetch_url", lambda *args, **kwargs: oversized_html)
    monkeypatch.setattr(trafilatura, "extract", mock_extract)

    with pytest.raises(WebFetchError):
        extract_web_page("https://example.com/huge-page")

    mock_extract.assert_not_called()


@pytest.mark.parametrize(
    "empty_extract_output",
    [
        None,
        "",
        "   ",
        json.dumps({"text": ""}),
        json.dumps({"text": None, "title": "Empty Page"}),
    ],
)
def test_extract_web_page_empty_extraction_raises(
    empty_extract_output: str | None, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that an HTML page containing no extractable text raises WebEmptyContentError."""
    target_url = "https://paywall-or-spa.example.com"
    fake_html = "<html><body><script>loadReactApp();</script></body></html>"

    monkeypatch.setattr(trafilatura, "fetch_url", lambda *args, **kwargs: fake_html)
    monkeypatch.setattr(trafilatura, "extract", lambda *args, **kwargs: empty_extract_output)

    with pytest.raises(WebEmptyContentError) as exc_info:
        extract_web_page(target_url)

    assert target_url in str(exc_info.value)
    assert exc_info.value.url == target_url


def test_extract_web_page_unexpected_exception_propagates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that unexpected system/programming errors (e.g. MemoryError) propagate unwrapped."""
    target_url = "https://example.com/article"

    def mock_fetch_out_of_memory(*args: object, **kwargs: object) -> None:
        raise MemoryError("Out of memory in native allocator")

    monkeypatch.setattr(trafilatura, "fetch_url", mock_fetch_out_of_memory)

    with pytest.raises(MemoryError):
        extract_web_page(target_url)


def test_compute_content_hash_deterministic() -> None:
    """Verify that compute_content_hash produces consistent SHA-256 digests."""
    text1 = "Neural network attention mechanisms for query retrieval."
    text2 = "Neural network attention mechanisms for query retrieval."
    text3 = "Different textual contents generate differing digest values."

    hash1 = compute_content_hash(text1)
    hash2 = compute_content_hash(text2)
    hash3 = compute_content_hash(text3)

    assert hash1 == hash2
    assert len(hash1) == 64
    assert hash1 != hash3


@pytest.mark.parametrize(
    "valid_url",
    [
        "http://example.com",
        "https://example.com",
        "https://sub.domain.co.uk/path/to/resource?query=1#anchor",
        "http://localhost:8000/api/v1",
        "https://127.0.0.1:8080",
    ],
)
def test_validate_url_accepts_http_and_https(valid_url: str) -> None:
    """Verify that _validate_url accepts valid http and https URLs."""
    assert _validate_url(valid_url) == valid_url


@pytest.mark.parametrize(
    "malformed_url",
    [
        "example.com",
        "ftp://files.example.com",
        "mailto:user@example.com",
        "javascript:alert(1)",
        "http://",
        "https://",
        "",
        "   ",
        None,
    ],
)
def test_validate_url_rejects_malformed(malformed_url: str) -> None:
    """Verify that _validate_url raises InvalidURLError on invalid inputs."""
    with pytest.raises(InvalidURLError):
        _validate_url(malformed_url)  # type: ignore[arg-type]
