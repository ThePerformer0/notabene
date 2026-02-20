import click
from notabene.core.database import get_database, init_database
from notabene.core.config import get_config, init_config
from notabene.managers.knowledge_organizer import KnowledgeOrganizer
from notabene.cli.display import console, print_success, print_error

@click.group()
def tag():
    """Manage tags."""
    init_config()
    try:
        get_database()
    except RuntimeError:
        config = get_config()
        init_database(config.db_path)

@tag.command()
@click.argument("source_id", type=int)
@click.argument("tag_name")
def add(source_id, tag_name):
    """Add a tag to a source."""
    db = get_database()
    with next(db.get_session()) as session:
        manager = KnowledgeOrganizer(session)
        try:
            manager.add_tag(source_id, tag_name)
            print_success(f"Tag '#{tag_name}' added to source {source_id}")
        except Exception as e:
            print_error(f"Failed to add tag: {e}")
