"""Robust web page extraction module for NotaBene using trafilatura.

This module provides functions and data structures for downloading web pages,
validating URLs, and extracting main text content and document metadata (title,
author, site name, publication date). It performs extraction only, with no
summarization, OCR, or embedding logic.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import logging
from urllib.parse import urlparse

import requests
import trafilatura
import trafilatura.settings
import urllib3

from notabene.ingestion.exceptions import (
    InvalidURLError,
    WebEmptyContentError,
    WebFetchError,
)

logger = logging.getLogger("notabene.ingestion.web")

_MAX_CONTENT_SIZE_BYTES: int = 20 * 1024 * 1024  # 20 MB
_DEFAULT_USER_AGENT: str = "NotaBene/0.1 (Academic Research Assistant; local personal use)"


@dataclass(frozen=True)
class ExtractedWebPage:
    """Structured representation of an extracted web page.

    Attributes:
        url: Normalized target URL actually requested.
        title: Page or article title, or None if unavailable.
        author: Author or creator name, or None if unavailable.
        site_name: Website or publisher name, or None if unavailable.
        publish_date: ISO 8601 publication date string if available, otherwise None.
        text: Cleaned main body text of the article/page.
        content_hash: Hexadecimal SHA-256 digest of the extracted text.
        extracted_at: UTC timestamp when extraction was completed.
    """

    url: str
    title: str | None
    author: str | None
    site_name: str | None
    publish_date: str | None
    text: str
    content_hash: str
    extracted_at: datetime


def _clean_metadata_field(value: str | None) -> str | None:
    """Clean and normalize a metadata string value.

    Args:
        value: Raw metadata field string value or None.

    Returns:
        Stripped string if non-empty, otherwise None.
    """
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned if cleaned else None


def compute_content_hash(text: str) -> str:
    """Compute the SHA-256 hexadecimal hash of extracted text normalized in UTF-8.

    Args:
        text: Extracted plain text content.

    Returns:
        Hexadecimal SHA-256 string representation.
    """
    normalized = text.strip()
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    logger.debug("Computed content SHA-256 (%d chars): %s", len(normalized), digest)
    return digest


def _validate_url(url: str) -> str:
    """Validate that a URL is well-formed with an http/https scheme and a host.

    Args:
        url: Raw URL string.

    Returns:
        The validated URL string stripped of surrounding whitespace.

    Raises:
        InvalidURLError: If the URL is empty, not a string, lacks an http(s)
            scheme, or lacks a network location (domain).
    """
    if not isinstance(url, str) or not url.strip():
        logger.warning("URL validation failed: empty or non-string input: %r", url)
        raise InvalidURLError(str(url), "URL must be a non-empty string")

    cleaned_url = url.strip()
    try:
        parsed = urlparse(cleaned_url)
    except Exception as err:
        logger.warning("URL parsing failed for '%s': %s", cleaned_url, err)
        raise InvalidURLError(cleaned_url, f"Malformed URL syntax: {err}") from err

    scheme = parsed.scheme.lower()
    if scheme not in ("http", "https"):
        logger.warning("URL validation rejected non-http scheme '%s' for %s", scheme, cleaned_url)
        raise InvalidURLError(
            cleaned_url,
            f"Unsupported scheme '{scheme}'. Only http:// and https:// are permitted.",
        )

    if not parsed.netloc:
        logger.warning("URL validation rejected missing domain for %s", cleaned_url)
        raise InvalidURLError(cleaned_url, "Missing host/domain name in URL")

    return cleaned_url


def extract_web_page(url: str, timeout: float = 15.0) -> ExtractedWebPage:
    """Download and extract the main content and metadata from a web page.

    Args:
        url: The web URL to fetch and parse.
        timeout: Maximum seconds allowed for network operations (default: 15.0).

    Returns:
        An ExtractedWebPage dataclass instance populated with extracted data.

    Raises:
        InvalidURLError: If the URL is invalid or malformed.
        WebFetchError: If downloading fails due to network, timeout, HTTP errors,
            or if the downloaded content exceeds the size limit.
        WebEmptyContentError: If the page was fetched but contains no extractable text.
    """
    validated_url = _validate_url(url)
    logger.debug("Fetching web page from URL: %s (timeout=%.1fs)", validated_url, timeout)

    config = trafilatura.settings.use_config()
    config.set("DEFAULT", "MAX_FILE_SIZE", str(_MAX_CONTENT_SIZE_BYTES))
    config.set("DEFAULT", "USER_AGENT", _DEFAULT_USER_AGENT)
    config.set("DEFAULT", "TIMEOUT", str(round(timeout)))

    try:
        downloaded_html = trafilatura.fetch_url(validated_url, config=config)
    except (
        requests.exceptions.Timeout,
        urllib3.exceptions.TimeoutError,
        TimeoutError,
    ) as err:
        logger.warning("Timeout fetching web page %s: %s", validated_url, err)
        raise WebFetchError(validated_url, "Request timed out", cause=err) from err
    except (
        requests.exceptions.ConnectionError,
        requests.exceptions.RequestException,
        urllib3.exceptions.HTTPError,
    ) as err:
        logger.warning("Network failure fetching web page %s: %s", validated_url, err)
        raise WebFetchError(validated_url, f"Network request failed: {err}", cause=err) from err

    if downloaded_html is None:
        logger.warning("Trafilatura fetch_url returned None for %s", validated_url)
        raise WebFetchError(
            validated_url,
            "Failed to download web page content (fetch returned empty/None)",
        )

    content_size = len(downloaded_html.encode("utf-8"))
    if content_size > _MAX_CONTENT_SIZE_BYTES:
        logger.warning(
            "Downloaded content exceeds size limit for %s: %d bytes > %d bytes",
            validated_url,
            content_size,
            _MAX_CONTENT_SIZE_BYTES,
        )
        raise WebFetchError(
            validated_url,
            f"Response size ({content_size} bytes) exceeds maximum allowed "
            f"({_MAX_CONTENT_SIZE_BYTES} bytes)",
        )

    logger.debug("Extracting content and metadata from HTML (%d bytes)", content_size)

    raw_extract = trafilatura.extract(
        downloaded_html,
        output_format="json",
        with_metadata=True,
        url=validated_url,
        config=config,
    )

    if raw_extract is None:
        logger.warning("Trafilatura extract returned None for %s", validated_url)
        raise WebEmptyContentError(validated_url)

    if isinstance(raw_extract, dict):
        data = raw_extract
    elif isinstance(raw_extract, str):
        try:
            data = json.loads(raw_extract)
        except (json.JSONDecodeError, ValueError):
            data = {"text": raw_extract}
    else:
        data = {"text": str(raw_extract)}

    text_val = data.get("text")
    if text_val is None or not str(text_val).strip():
        logger.warning("Extracted text is empty for %s", validated_url)
        raise WebEmptyContentError(validated_url)

    extracted_text = str(text_val).strip()
    title = _clean_metadata_field(data.get("title"))
    author = _clean_metadata_field(data.get("author"))
    site_name = _clean_metadata_field(
        data.get("sitename")
        or data.get("source-hostname")
        or data.get("hostname")
        or data.get("source")
    )
    publish_date = _clean_metadata_field(data.get("date"))

    content_hash = compute_content_hash(extracted_text)
    extracted_at = datetime.now(timezone.utc)

    logger.debug(
        "Successfully extracted web page: %s (title=%r, chars=%d)",
        validated_url,
        title,
        len(extracted_text),
    )

    return ExtractedWebPage(
        url=validated_url,
        title=title,
        author=author,
        site_name=site_name,
        publish_date=publish_date,
        text=extracted_text,
        content_hash=content_hash,
        extracted_at=extracted_at,
    )
