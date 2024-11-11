import typer
import pyperclip
import json
import validators
from pathlib import Path
from openai import OpenAI
from rich import print
from typing_extensions import Annotated
from .blog_parser import BlogPostParser

from .helper import POST_REVIEWER_CONTENT, DESCRIPTION_GENERATOR_CONTENT, EXCERPT_GENERATOR_CONTENT, TITLE_GENERATOR_CONTENT

overview = """
Swiss Army Knife (sak).

The following env vars need to exist: OPENAI_API_KEY, MEDIUM_API_KEY
"""

app = typer.Typer(no_args_is_help=True, help=overview)


@app.command()
def review(
    filepath: Annotated[
        Path, typer.Argument(help="The filepath of the blog post being reviewed.")
    ],
):
    """
    Send the blog post specified in FILEPATH to ChatGPT for review.
    """
    user_content = filepath.open().read()
    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": POST_REVIEWER_CONTENT},
            {"role": "user", "content": f"Analyse this article: ```{user_content}```"},
        ],
    )

    print(completion.choices[0].message.content)


@app.command()
def describe(
        filepath: Annotated[
        Path, typer.Argument(help="The filepath of the blog post being described.")
    ],
):
    """
    Send the blog post specified in FILEPATH to ChatGPT to summarise into a one-line description. The result is copied to your clipboard.
    """
    user_content = filepath.open().read()
    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": DESCRIPTION_GENERATOR_CONTENT},
            {"role": "user", "content": f"Summarise this article: ```{user_content}```"},
        ],
    )

    try:
        descriptions = json.loads(completion.choices[0].message.content)
    except json.JSONDecodeError:
        print("Response was not in JSON format...")
        raise typer.Abort()

    for i, description in enumerate(descriptions, start=1):
        print(f"[bold underline sky_blue1]Description {i}[/]\n{description}\n")

    selection = int(typer.prompt("Which description would you like to copy?"))

    pyperclip.copy(descriptions[selection - 1])


@app.command()
def title(
        filepath: Annotated[
        Path, typer.Argument(help="The filepath of the blog post being titled.")
    ],
):
    """
    Send the blog post specified in FILEPATH to ChatGPT to generate a title. The result is copied to your clipboard.
    """
    user_content = filepath.open().read()
    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": TITLE_GENERATOR_CONTENT},
            {"role": "user", "content": f"Create a title this article: ```{user_content}```"},
        ],
    )

    try:
        titles = json.loads(completion.choices[0].message.content)
    except json.JSONDecodeError:
        print("Response was not in JSON format...")
        raise typer.Abort()

    for i, title in enumerate(titles, start=1):
        print(f"[bold underline sky_blue1]Title {i}[/]\n{title}\n")

    selection = int(typer.prompt("Which title would you like to copy?"))

    pyperclip.copy(titles[selection - 1])



@app.command()
def introduce(
        filepath: Annotated[
        Path, typer.Argument(help="The filepath of the blog post being introduced (generate an excerpt).")
    ],
):
    """
    Send the blog post specified in FILEPATH to ChatGPT to generate an excerpt that can be used as the post's introduction. The chosen excerpt is copied to your clipboard.
    """
    user_content = filepath.open().read()
    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": EXCERPT_GENERATOR_CONTENT},
            {"role": "user", "content": f"Introduce this article: ```{user_content}```"},
        ],
    )

    try:
        exceprts = json.loads(completion.choices[0].message.content)
    except json.JSONDecodeError:
        print("Response was not in JSON format...")
        raise typer.Abort()

    for i, excerpt in enumerate(exceprts, start=1):
        print(f"[bold underline dark_orange]Excerpt {i}[/]\n{excerpt}\n")

    selection = int(typer.prompt("Which except would you like to copy?"))

    pyperclip.copy(exceprts[selection - 1])


@app.command()
def publish(
        blog_filepath: Annotated[
            Path, typer.Argument(help="The local filepath of the markdown file of the blog post being published.")
        ],
        canonical_url: Annotated[
            str, typer.Argument(help="The URL of the original blog post.")
        ],
        dry_run: Annotated[
            bool, typer.Option(help="If true, then the draft posts will be generated and written to file only. Nothing is posted to dev.to or Medium.")
        ] = False,
        only_medium: Annotated[
            bool, typer.Option(help="If true, then only Medium is posted to.")
        ] = False,
        only_dev: Annotated[
            bool, typer.Option(help="If true, then only Dev.to is posted to.")
        ] = False,
):
    """Publish draft blog posts on Dev.to and Medium of the specified markdown blog post file."""

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
        print("REMEMBER: Copy and paste the version from [bold blue]Medium[/bold blue] into [bold yellow]LinkedIn[/bold yellow]")