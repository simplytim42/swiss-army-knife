import typer

from importlib.metadata import version


app = typer.Typer()

__app_name__ = "sak"

try:
    __version__ = version(__app_name__)
except Exception:
    __version__ = "unknown"


@app.command()
def version():
    typer.echo(f"{__app_name__} version {__version__}")
    typer.Exit()
