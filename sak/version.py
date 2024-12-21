import typer
from rich import print
from importlib.metadata import version
from .utils import APP_NAME


app = typer.Typer()

try:
    __VERSION__ = version(APP_NAME)
except Exception:
    __VERSION__ = "unknown"


@app.command()
def version():
    print(f"{APP_NAME} version [bold yellow]{__VERSION__}[/bold yellow]")
    typer.Exit()
