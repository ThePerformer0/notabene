import click
from notabene.core.database import get_database, init_database
from notabene.core.config import get_config, init_config
from notabene.models.base import Source
from notabene.models.pdf import PDFDocument
from notabene.models.web import WebSource
from notabene.cli.display import console, print_error
from rich.panel import Panel
from rich.markdown import Markdown
from rich.columns import Columns

@click.command()
@click.argument("id", type=int)
def show(id):
    """Show details of a source."""
    init_config()
    try:
        get_database()
    except RuntimeError:
        config = get_config()
        init_database(config.db_path)

    db = get_database()
    with next(db.get_session()) as session:
        source = session.query(Source).filter(Source.id == id).first()
        
        if not source:
            print_error(f"Source with ID {id} not found.")
            return

        # Header info
        console.print(f"\n[bold white underline]{source.title}[/bold white underline]")
        console.print(f"[dim]Type: {source.type.upper()} | Added: {source.date_added.strftime('%Y-%m-%d')}[/dim]\n")
        
        if source.authors:
            console.print(f"[key]Authors:[/key] {source.authors}")
        
        # Specific fields
        if isinstance(source, PDFDocument):
            if source.year: console.print(f"[key]Year:[/key] {source.year}")
            if source.journal: console.print(f"[key]Journal:[/key] {source.journal}")
            if source.file_path: console.print(f"[key]File:[/key] [dim]{source.file_path}[/dim]")
            if source.abstract:
                console.print("\n[bold]Abstract[/bold]")
                console.print(Panel(source.abstract, border_style="dim", expand=False))

        elif isinstance(source, WebSource):
            if source.url: console.print(f"[key]URL:[/key] [link={source.url}]{source.url}[/link]")
            if source.domain: console.print(f"[key]Domain:[/key] {source.domain}")

        # Tags
        if source.tags:
            tags = [f"#{t.name}" for t in source.tags]
            console.print(f"\n[key]Tags:[/key] [cyan]{' '.join(tags)}[/cyan]")

        # Notes
        if source.notes:
            console.print("\n[bold]Notes[/bold]")
            for note in source.notes:
                # Custom styling for notes without icons per request (implied by minimal style)
                # or just use text indicators
                n_type = note.note_type.name
                
                # Minimalist note display
                console.print(f"[dim]-- {n_type} --[/dim]")
                console.print(note.content)
                console.print("")
