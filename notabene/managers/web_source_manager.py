"""Management of Web sources."""
import logging
from typing import List, Optional
from urllib.parse import urlparse
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from notabene.models.web import WebSource
from notabene.core.config import get_config

logger = logging.getLogger(__name__)


class WebSourceManager:
    """Manager for web sources."""

    def __init__(self, session: Session):
        """
        Initialize the manager.

        Args:
            session: Database session
        """
        self.session = session
        self.config = get_config()

    def add_web_source(self, url: str, auto_extract: bool = True) -> WebSource:
        """
        Add a web source to the database.

        Args:
            url: URL of the web source
            auto_extract: Whether to automatically extract metadata

        Returns:
            Added WebSource instance
        """
        # Validate URL
        parsed_url = urlparse(url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            raise ValueError(f"Invalid URL: {url}")

        # Check if already exists
        existing = self.session.query(WebSource).filter(WebSource.url == url).first()
        if existing:
            return existing

        web = WebSource(
            url=url,
            title=url,  # Placeholder
            domain=parsed_url.netloc,
            date_accessed=datetime.utcnow()
        )

        if auto_extract:
            self.extract_metadata(web)

        self.session.add(web)
        self.session.commit()
        return web

    def extract_metadata(self, web: WebSource):
        """
        Extract metadata from a web page.

        Args:
            web: WebSource instance
        """
        timeout = self.config.get("extraction.web.timeout", 30)
        user_agent = self.config.get("extraction.web.user_agent", "NotaBene/0.1.0")

        try:
            headers = {"User-Agent": user_agent}
            response = requests.get(web.url, headers=headers, timeout=timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract Title
            if soup.title and soup.title.string:
                web.title = soup.title.string.strip()
            elif soup.find("h1"):
                web.title = soup.find("h1").get_text().strip()

            # Extract Authors (common meta tags)
            author_tag = (
                soup.find("meta", attrs={"name": "author"}) or
                soup.find("meta", attrs={"property": "article:author"}) or
                soup.find("meta", attrs={"name": "twitter:creator"})
            )
            if author_tag and author_tag.get("content"):
                web.authors = author_tag["content"]

            # Extract Publication Date
            date_tag = (
                soup.find("meta", attrs={"property": "article:published_time"}) or
                soup.find("meta", attrs={"name": "pubdate"}) or
                soup.find("meta", attrs={"name": "date"})
            )
            if date_tag and date_tag.get("content"):
                try:
                    # Simple ISO parsing, might need more robust parser later
                    from dateutil.parser import parse
                    web.date_published = parse(date_tag["content"])
                except Exception:
                    logger.warning(f"Failed to parse date for {web.url}")

        except Exception as e:
            logger.error(f"Error extracting metadata from {web.url}: {e}")

    def get_web_source(self, web_id: int) -> Optional[WebSource]:
        """Get a web source by ID."""
        return self.session.query(WebSource).filter(WebSource.id == web_id).first()

    def list_web_sources(self) -> List[WebSource]:
        """List all web sources."""
        return self.session.query(WebSource).all()

    def delete_web_source(self, web_id: int):
        """Delete a web source."""
        web = self.get_web_source(web_id)
        if web:
            self.session.delete(web)
            self.session.commit()
