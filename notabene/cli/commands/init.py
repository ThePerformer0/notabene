import click
from notabene.core.config import init_config
from notabene.core.database import init_database
from notabene.cli.display import console, print_success, print_info

@click.command()
def init():
    """Initialize NotaBene configuration and database."""
    print_info("Initializing NotaBene environment...")
    
    # Initialize Config
    config = init_config()
    print_success(f"Configuration loaded/created at: [value]{config.config_path}[/value]")
    
    # Initialize Database
    db = init_database(config.db_path)
    print_success(f"Database initialized at: [value]{config.db_path}[/value]")
    
    console.print("\n[info]You are ready to start adding sources.[/info]")
