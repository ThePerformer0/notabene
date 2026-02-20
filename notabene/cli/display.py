from rich.console import Console
from rich.theme import Theme

# Custom theme for "The Performer" - minimalist and clean
# No emojis, just colors and styles
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "error": "bold red",
    "success": "green",
    "header": "bold white underline",
    "highlight": "bold cyan",
    "key": "dim yellow",
    "value": "white"
})

console = Console(theme=custom_theme)

def print_logo():
    """Print the user-provided NotaBene ASCII logo."""
    # Custom logo provided by The Performer
    logo = r"""
[bold cyan]███╗   ██╗ ██████╗ ████████╗ █████╗ ██████╗ ███████╗███╗   ██╗███████╗
████╗  ██║██╔═══██╗╚══██╔══╝██╔══██╗██╔══██╗██╔════╝████╗  ██║██╔════╝
██╔██╗ ██║██║   ██║   ██║   ███████║██████╔╝█████╗  ██╔██╗ ██║█████╗  
██║╚██╗██║██║   ██║   ██║   ██╔══██║██╔══██╗██╔══╝  ██║╚██╗██║██╔══╝  
██║ ╚████║╚██████╔╝   ██║   ██║  ██║██████╔╝███████╗██║ ╚████║███████╗
╚═╝  ╚═══╝ ╚═════╝    ╚═╝   ╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═══╝╚══════╝[/bold cyan]
                                                                    
[dim]══════════════════════════════════════════════════════════════════
 Research Knowledge Base                  by  The Performer  ◆
══════════════════════════════════════════════════════════════════[/dim]
    """
    console.print(logo)

def print_error(message: str):
    """Print an error message."""
    console.print(f"[error]ERROR:[/error] {message}")

def print_success(message: str):
    """Print a success message."""
    console.print(f"[success]SUCCESS:[/success] {message}")

def print_info(message: str):
    """Print an info message."""
    console.print(f"[info]{message}[/info]")
