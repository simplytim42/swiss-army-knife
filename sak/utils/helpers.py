import typer
from rich import print

OPEN_AI_MODELS = [
    "gpt-4o",
    "gpt-4o-mini",
    "o1",
    "o1-mini",
]


def validate_model(model: str):
    if model not in OPEN_AI_MODELS:
        print(f"[bold red]Error: '{model}' is not a valid model.")
        raise typer.Exit(code=1)
