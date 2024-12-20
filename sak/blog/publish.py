import typer
from typing_extensions import Annotated
from pathlib import Path
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
import validators
from .blog_parser import BlogPostParser

app = typer.Typer()


@app.command()
def publish(
    blog_filepath: Annotated[
        Path,
        typer.Argument(
            help="The local filepath of the markdown file of the blog post being published."
        ),
    ],
    canonical_url: Annotated[
        str, typer.Argument(help="The URL of the original blog post.")
    ],
    dry_run: Annotated[
        bool,
        typer.Option(
            help="If true, then the draft posts will be generated and written to file only. Nothing is posted to dev.to or Medium."
        ),
    ] = False,
    only_medium: Annotated[
        bool, typer.Option(help="If true, then only Medium is posted to.")
    ] = False,
    only_dev: Annotated[
        bool, typer.Option(help="If true, then only Dev.to is posted to.")
    ] = False,
):
    """Publish a draft blog posts on Dev.to and Medium."""
    with Progress(
        SpinnerColumn(style="purple3"),
        TextColumn("[bold purple3]Publishing blog post..."),
        transient=True,
    ) as progress:
        progress.add_task("")
        if not validators.url(canonical_url):
            raise Exception("The Canonical URL you provided is not valid.")

        if not blog_filepath.exists():
            raise Exception("The filepath provided does not exist.")

        if only_dev and only_medium:
            raise Exception("--only-dev and --only-medium cannot be called together.")

        post = BlogPostParser(blog_filepath.read_text())

        if not only_dev:
            post.send_to_medium(canonical_url, dry_run)

        if not only_medium:
            post.send_to_dev(canonical_url, dry_run)

        if not dry_run:
            print(
                "REMEMBER: Copy and paste the version from [bold blue]Medium[/bold blue] into [bold yellow]LinkedIn[/bold yellow]"
            )
