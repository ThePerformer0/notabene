import click
from notabene.core.database import get_database, init_database
from notabene.core.config import get_config, init_config
from notabene.managers.document_manager import DocumentManager
from notabene.managers.web_source_manager import WebSourceManager
from notabene.cli.display import console
from rich.table import Table

@click.command()
@click.option("--type", "-t", type=click.Choice(["pdf", "web", "all"]), default="all", help="Filter by source type")
def list_sources(type):
    """List all sources."""
    # Ensure config and db
    init_config()
    try:
        get_database()
    except RuntimeError:
        config = get_config()
        init_database(config.db_path)
    
    db = get_database()
    sources = []
    
    with next(db.get_session()) as session:
        if type in ["pdf", "all"]:
             doc_mgr = DocumentManager(session)
             sources.extend(doc_mgr.list_pdfs())
        
        if type in ["web", "all"]:
             web_mgr = WebSourceManager(session)
             sources.extend(web_mgr.list_web_sources())
        
        if not sources:
            console.print("[info]No sources found.[/info]")
            return

        # Sort by date added (newest first)
        sources.sort(key=lambda x: x.date_added, reverse=True)

        table = Table(show_header=True, header_style="bold white", box=None, padding=(0, 2))
        table.add_column("ID", style="dim", justify="right")
        table.add_column("Type", width=4)
        table.add_column("Title", style="bold")
        table.add_column("Authors", style="dim cyan")
        table.add_column("Date", style="dim")

        for source in sources:
            s_type = "[blue]PDF[/blue]" if source.type == "pdf" else "[green]WEB[/green]"
            date_str = source.date_added.strftime("%Y-%m-%d")
            authors = source.authors[:30] + "..." if source.authors and len(source.authors) > 30 else (source.authors or "")
            
            table.add_row(
                str(source.id),
                s_type,
                source.title,
                authors,
                date_str
            )

        console.print(table)
