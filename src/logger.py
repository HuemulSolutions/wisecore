from rich.console import Console
from rich.theme import Theme
from rich.logging import RichHandler
import logging

custom_theme = Theme({
    "error": "bold red",
    "warning": "yellow",
    "info": "cyan",
    "debug": "dim",
})

console = Console(theme=custom_theme, stderr=True)

def setup_logging(level: str = "INFO"):
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, show_path=False, rich_tracebacks=True)]
    )
    return logging.getLogger("app")