import click
from pathlib import Path

from notabene.core.database import get_database, init_database
from notabene.core.config import get_config, init_config
from notabene.managers.document_manager import DocumentManager
from notabene.managers.web_source_manager import WebSourceManager
from notabene.cli.display import print_success, print_error, print_info, console

@click.group()
def add():
    """Add a new source (PDF or Web)."""
    # Ensure config and db are loaded
    init_config()
    try:
        get_database()
    except RuntimeError:
        # If not initialized, try to initialize with default config
        config = get_config()
        init_database(config.db_path)

@add.command()
@click.argument("filepath", type=click.Path(exists=True, path_type=Path))
@click.option("--no-extract", is_flag=True, help="Skip metadata extraction")
def pdf(filepath, no_extract):
    """Add a PDF file."""
    print_info(f"Adding PDF: [value]{filepath.name}[/value]")
    
    db = get_database()
    with next(db.get_session()) as session:
        manager = DocumentManager(session)
        try:
            doc = manager.add_pdf(filepath, auto_extract=not no_extract)
            print_success(f"PDF added: [highlight]{doc.title}[/highlight] (ID: {doc.id})")
            if doc.authors:
                 console.print(f"  [key]Authors:[/key] {doc.authors}")
            if doc.year:
                 console.print(f"  [key]Year:[/key] {doc.year}")
        except Exception as e:
            print_error(f"Failed to add PDF: {e}")

@add.command()
@click.argument("url")
@click.option("--no-extract", is_flag=True, help="Skip metadata extraction")
def web(url, no_extract):
    """Add a Web source from URL."""
    print_info(f"Adding URL: [value]{url}[/value]")
    
    db = get_database()
    with next(db.get_session()) as session:
        manager = WebSourceManager(session)
        try:
            source = manager.add_web_source(url, auto_extract=not no_extract)
            print_success(f"Web source added: [highlight]{source.title}[/highlight] (ID: {source.id})")
            if source.authors:
                 console.print(f"  [key]Authors:[/key] {source.authors}")
        except Exception as e:
            print_error(f"Failed to add Web source: {e}")
