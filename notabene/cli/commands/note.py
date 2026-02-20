import click
from notabene.core.database import get_database, init_database
from notabene.core.config import get_config, init_config
from notabene.managers.note_manager import NoteManager
from notabene.models.note import NoteType
from notabene.cli.display import console, print_success, print_error

@click.group()
def note():
    """Manage notes."""
    init_config()
    try:
        get_database()
    except RuntimeError:
        config = get_config()
        init_database(config.db_path)

@note.command()
@click.argument("source_id", type=int)
@click.argument("content")
@click.option("--type", "-t", type=click.Choice(["general", "idea", "argument", "question", "quote"]), default="general")
def add(source_id, content, type):
    """Add a note to a source."""
    db = get_database()
    with next(db.get_session()) as session:
        manager = NoteManager(session)
        try:
            # Map string to enum
            if type == "idea": n_type = NoteType.IDEA
            elif type == "argument": n_type = NoteType.ARGUMENT
            elif type == "question": n_type = NoteType.QUESTION
            elif type == "quote": n_type = NoteType.QUOTE
            else: n_type = NoteType.GENERAL

            n = manager.add_note(source_id, content, n_type)
            print_success(f"Note added to source {source_id}")
        except Exception as e:
            print_error(f"Failed to add note: {e}")

@note.command()
@click.argument("source_id", type=int)
def list(source_id):
    """List notes for a source."""
    db = get_database()
    with next(db.get_session()) as session:
        manager = NoteManager(session)
        notes = manager.get_notes(source_id)
        
        if not notes:
            console.print("[dim]No notes found for this source.[/dim]")
            return

        for n in notes:
             console.print(f"[bold]{n.note_type.name}[/bold]: {n.content}")
