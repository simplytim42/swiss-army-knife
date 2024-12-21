from typing_extensions import Annotated
import typer
from pathlib import Path


class Annotations:
    filepath = Annotated[Path, typer.Argument(help="The filepath of the blog post.")]

    model = Annotated[str, typer.Option(help="The model you wish to use.")]
