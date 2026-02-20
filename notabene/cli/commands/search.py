import click
from notabene.core.database import get_database, init_database
from notabene.core.config import get_config, init_config
from notabene.managers.search_engine import SearchEngine
from notabene.cli.display import console, print_info

@click.command()
@click.argument("query")
def search(query):
    """Search sources by keyword."""
    init_config()
    try:
        get_database()
    except RuntimeError:
        config = get_config()
        init_database(config.db_path)

    db = get_database()
    with next(db.get_session()) as session:
        engine = SearchEngine(session)
        print_info(f"Searching for: '[bold]{query}[/bold]'...")
        
        results = engine.search(query)
        
        if not results:
            console.print("[dim]No results found.[/dim]")
            return

        for source in results:
            console.print(f"[bold cyan]{source.id}[/bold cyan] [white]{source.title}[/white] [dim]({source.type})[/dim]")
