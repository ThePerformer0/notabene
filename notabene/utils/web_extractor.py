import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional, Any
from urllib.parse import urlparse

def extract_metadata(url: str) -> Dict[str, Any]:
    """
    Extracts metadata from a Web URL.

    Args:
        url (str): The URL of the web page.

    Returns:
        Dict[str, Any]: A dictionary containing extracted metadata
                        (title, author, description, site_name).
    """
    metadata: Dict[str, Any] = {
        "title": None,
        "authors": None,
        "description": None,
        "site_name": None,
        "url": url
    }

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Title
        if soup.title:
            metadata["title"] = soup.title.string.strip()
        
        # Try Open Graph tags for better metadata
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            metadata["title"] = og_title["content"]

        og_site_name = soup.find("meta", property="og:site_name")
        if og_site_name and og_site_name.get("content"):
            metadata["site_name"] = og_site_name["content"]
        else:
            metadata["site_name"] = urlparse(url).netloc

        og_description = soup.find("meta", property="og:description")
        if og_description and og_description.get("content"):
            metadata["description"] = og_description["content"]
        else:
            description = soup.find("meta", attrs={"name": "description"})
            if description and description.get("content"):
                metadata["description"] = description["content"]

        # Author
        author = soup.find("meta", attrs={"name": "author"})
        if author and author.get("content"):
            metadata["authors"] = author["content"]
            
    except Exception as e:
        print(f"Error extracting metadata from URL {url}: {e}")
        metadata["error"] = str(e)
        
    return metadata
