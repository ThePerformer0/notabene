import click
import os
from notabene.core.database import get_database, init_database
from notabene.core.config import get_config, init_config
from notabene.managers.document_manager import DocumentManager
from notabene.managers.web_source_manager import WebSourceManager
from notabene.utils.bibtex_exporter import export_to_bibtex
from notabene.utils.markdown_exporter import export_to_markdown
from notabene.cli.display import console, print_success, print_error, print_info

@click.group()
def export():
    """Export sources."""
    init_config()
    try:
        get_database()
    except RuntimeError:
        config = get_config()
        init_database(config.db_path)

@export.command()
@click.option("--output", "-o", default="library.bib", help="Output file path")
def bibtex(output):
    """Export to BibTeX."""
    db = get_database()
    sources = []
    with next(db.get_session()) as session:
        doc_mgr = DocumentManager(session)
        web_mgr = WebSourceManager(session)
        sources.extend(doc_mgr.list_pdfs())
        sources.extend(web_mgr.list_web_sources())
        
        try:
            print_info(f"Exporting {len(sources)} sources to {output}...")
            export_to_bibtex(sources, output)
            print_success(f"Export complete: [value]{os.path.abspath(output)}[/value]")
        except Exception as e:
            print_error(f"Export failed: {e}")

@export.command()
@click.option("--output", "-o", default="notes.md", help="Output file path")
def markdown(output):
    """Export to Markdown."""
    db = get_database()
    sources = []
    with next(db.get_session()) as session:
        doc_mgr = DocumentManager(session)
        web_mgr = WebSourceManager(session)
        sources.extend(doc_mgr.list_pdfs())
        sources.extend(web_mgr.list_web_sources())
        
        try:
            print_info(f"Exporting notes to {output}...")
            export_to_markdown(sources, output)
            print_success(f"Export complete: [value]{os.path.abspath(output)}[/value]")
        except Exception as e:
            print_error(f"Export failed: {e}")
