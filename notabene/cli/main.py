import click
import click
from notabene.cli.display import console, print_logo

class Section(click.Group):
    """Custom help group to organize commands."""
    def format_help(self, ctx, formatter):
        print_logo()
        console.print("")
        super().format_help(ctx, formatter)

@click.group(cls=Section)
@click.version_option(version="0.1.0", prog_name="notabene")
def cli():
    """
    NotaBene: A CLI tool for organizing research sources and notes.
    
    Managed by: The Performer
    """
    pass

# Import commands
from notabene.cli.commands import init
from notabene.cli.commands import add
from notabene.cli.commands import list_src
from notabene.cli.commands import show
from notabene.cli.commands import search
from notabene.cli.commands import note
from notabene.cli.commands import tag
from notabene.cli.commands import export

# Add commands to CLI
cli.add_command(init.init)
cli.add_command(add.add)
cli.add_command(list_src.list_sources, name="list")
cli.add_command(show.show)
cli.add_command(search.search)
cli.add_command(note.note)
cli.add_command(tag.tag)
cli.add_command(export.export)

if __name__ == "__main__":
    cli()
