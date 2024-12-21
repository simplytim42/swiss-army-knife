import typer
from rich import print
from pathlib import Path

class Helpers:
    @staticmethod()
    def validate_model(model: str):
        models = [
            "gpt-4o",
            "gpt-4o-mini",
            "o1",
            "o1-mini",
        ]
        if model not in models:
            print(f"[bold red]Error: '{model}' is not a valid model.")
            raise typer.Exit(code=1)

    @staticmethod()
    def check_file_exists(filepath: Path):
        if not filepath.exists():
            print(f"[bold red]File not found:[/bold red] {filepath}")
            raise typer.Exit(code=1)