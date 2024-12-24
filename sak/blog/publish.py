import typer
from typing_extensions import Annotated
from rich import print
import validators
from .blog_parser import BlogPostParser
from ..utils import Annotations, Helpers

DEFAULT_URL = "http://default.com"

app = typer.Typer()


@app.command()
def publish(
    filepath: Annotations.filepath,
    canonical_url: Annotated[
        str, typer.Argument(help="The URL of the original blog post.")
    ] = DEFAULT_URL,
    dry_run: Annotated[
        bool,
        typer.Option(
            help="If true, then the draft posts will be written to file instead."
        ),
    ] = False,
    only_medium: Annotated[
        bool, typer.Option(help="If true, send post to Medium only.")
    ] = False,
    only_dev: Annotated[
        bool, typer.Option(help="If true, send post to Dev.to only.")
    ] = False,
):
    """Publish a draft blog posts on Dev.to and Medium."""
    with Helpers.get_spinner("Publishing blog post...") as progress:
        progress.add_task("")
        if not validators.url(canonical_url):
            raise Exception("The Canonical URL you provided is not valid.")

        Helpers.check_file_exists(filepath)

        if only_dev and only_medium:
            raise Exception("--only-dev and --only-medium cannot be called together.")

        post = BlogPostParser(filepath.read_text())

        if not only_dev:
            post.send_to_medium(canonical_url, dry_run)

        if not only_medium:
            post.send_to_dev(canonical_url, dry_run)

    if canonical_url == DEFAULT_URL:
        msg = f"[yellow bold]Warning:[/yellow bold] Using default canonical URL of {DEFAULT_URL}"
        print(msg)

    if not dry_run:
        msg = "REMEMBER: Copy and paste the version from [bold blue]Medium[/bold blue] into [bold yellow]LinkedIn[/bold yellow]"
        print(msg)
