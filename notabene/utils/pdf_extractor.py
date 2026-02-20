import os
from datetime import datetime
from typing import Dict, Optional, Any
import pdfplumber
from pathlib import Path

def extract_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extracts metadata from a PDF file.

    Args:
        filepath (str): Path to the PDF file.

    Returns:
        Dict[str, Any]: A dictionary containing extracted metadata 
                        (title, authors, creation_date, etc.).
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"PDF file not found: {filepath}")

    metadata: Dict[str, Any] = {
        "title": None,
        "authors": None,
        "creation_date": None,
        "page_count": 0,
        "original_metadata": {}
    }

    try:
        with pdfplumber.open(filepath) as pdf:
            pdf_info = pdf.metadata
            metadata["page_count"] = len(pdf.pages)
            metadata["original_metadata"] = pdf_info

            if pdf_info:
                # Attempt to extract title
                if "Title" in pdf_info and pdf_info["Title"]:
                    metadata["title"] = pdf_info["Title"]
                
                # Attempt to extract author
                if "Author" in pdf_info and pdf_info["Author"]:
                    metadata["authors"] = pdf_info["Author"]
                
                # Attempt to extract creation date
                # Format is usually like "D:20231024120000+02'00'"
                if "CreationDate" in pdf_info:
                    metadata["creation_date"] = pdf_info["CreationDate"]

    except Exception as e:
        print(f"Error extracting metadata from PDF {filepath}: {e}")
        # In a real app, we might want to log this or raise a custom exception
        
    # If title is missing, use filename
    if not metadata["title"]:
        metadata["title"] = Path(filepath).stem

    return metadata
