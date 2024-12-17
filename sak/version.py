import typer
from rich import print
from importlib.metadata import version
from .utils.config import __APP_NAME__


app = typer.Typer()

try:
    __VERSION__ = version(__APP_NAME__)
except Exception:
    __VERSION__ = "unknown"


@app.command()
def version():
    print(f"{__APP_NAME__} version [bold yellow]{__VERSION__}[/bold yellow]")
    typer.Exit()
