from typing import List
from notabene.models.base import Source
from notabene.models.pdf import PDFDocument
from notabene.models.web import WebSource

def export_to_bibtex(sources: List[Source], output_file: str) -> None:
    """
    Exports a list of sources to a BibTeX file.

    Args:
        sources (List[Source]): List of source objects to export.
        output_file (str): Path to the output BibTeX file.
    """
    bibtex_entries = []

    for i, source in enumerate(sources):
        entry_type = "misc"
        citation_key = f"source_{source.id}"
        
        # Try to generate a better citation key: AuthorYearTitle
        author_part = "Unknown"
        if source.authors:
            first_author = source.authors.split(",")[0].strip().split(" ")[-1]
            author_part = "".join(c for c in first_author if c.isalnum())
        
        year_part = "0000"
        if hasattr(source, "year") and source.year:
            year_part = source.year
        elif hasattr(source, "date_published") and source.date_published:
            year_part = str(source.date_published.year)
        elif source.date_added:
            year_part = str(source.date_added.year)

        title_part = "".join(c for c in source.title if c.isalnum())[:10]
        citation_key = f"{author_part}{year_part}{title_part}"
        
        # Ensure uniqueness (simple approach for now)
        citation_key = f"{citation_key}_{source.id}"

        fields = {
            "title": source.title,
            "author": source.authors or "Unknown",
        }

        if isinstance(source, PDFDocument):
            entry_type = "article" # Default assumption for PDFs
            if source.journal:
                fields["journal"] = source.journal
            if source.year:
                fields["year"] = source.year
            if source.doi:
                fields["doi"] = source.doi
            if source.abstract:
                fields["abstract"] = source.abstract
        
        elif isinstance(source, WebSource):
            entry_type = "misc"
            fields["howpublished"] = f"\\url{{{source.url}}}"
            if source.date_published:
                fields["year"] = str(source.date_published.year)
                fields["month"] = str(source.date_published.month)
            if source.date_accessed:
                fields["note"] = f"Accessed: {source.date_accessed.strftime('%Y-%m-%d')}"
            if source.domain:
                # Sometimes useful to put domain in organization or publisher
                pass

        # Format entry
        entry_str = f"@{entry_type}{{{citation_key},\n"
        for key, value in fields.items():
            if value:
                # Escape minimal characters usually needed in BibTeX (simple version)
                clean_value = str(value).replace("{", "\\{").replace("}", "\\}")
                entry_str += f"  {key} = {{{clean_value}}},\n"
        entry_str += "}\n"
        
        bibtex_entries.append(entry_str)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(bibtex_entries))
