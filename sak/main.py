import typer
import pyperclip
import json
from pathlib import Path
from openai import OpenAI
from rich import print
from typing_extensions import Annotated

from .helper import POST_REVIEWER_CONTENT, DESCRIPTION_GENERATOR_CONTENT, EXCERPT_GENERATOR_CONTENT


app = typer.Typer(no_args_is_help=True)


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
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": DESCRIPTION_GENERATOR_CONTENT},
            {"role": "user", "content": f"Summarise this article: ```{user_content}```"},
        ],
    )

    descriptions = json.loads(completion.choices[0].message.content)

    for i, description in enumerate(descriptions, start=1):
        print(f"[bold underline sky_blue1]Description {i}[/]\n{description}\n")

    selection = int(typer.prompt("Which description would you like to copy?"))

    pyperclip.copy(descriptions[selection - 1])



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

    exceprts = json.loads(completion.choices[0].message.content)

    for i, excerpt in enumerate(exceprts, start=1):
        print(f"[bold underline dark_orange]Excerpt {i}[/]\n{excerpt}\n")

    selection = int(typer.prompt("Which except would you like to copy?"))

    pyperclip.copy(exceprts[selection - 1])
