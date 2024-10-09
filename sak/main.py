import typer
from pathlib import Path
from openai import OpenAI
from rich import print
from typing_extensions import Annotated

from .helper import POST_REVIEWER_CONTENT


app = typer.Typer(no_args_is_help=True)


@app.command()
def post(
    filepath: Annotated[
        Path, typer.Argument(help="The filepath of the blog post being reviewed.")
    ],
):
    """
    Send the blog post specified in FILEPATH to ChatGPT for review.
    """
    with filepath.open() as f:
        user_content = f.read()

    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": POST_REVIEWER_CONTENT},
            {"role": "user", "content": f"Analyse this article: ```{user_content}```"},
        ],
    )

    print(completion.choices[0].message.content)
