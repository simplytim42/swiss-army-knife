import typer
from rich import print
import pyperclip
from ..utils import DEFAULT_AI_MODEL, Annotations, Helpers
from pydantic import BaseModel


class DescriptionResponse(BaseModel):
    descriptions: list[str]

DESCRIPTION_GENERATOR_CONTENT = """
You are a skilled, concise summariser specialising in technical blog posts and SEO. Articles provided within triple backticks are in markdown format (for 'Material for MKDocs') and may include front matter you can ignore.

Your task is to create **three distinct one-line summaries** that will pique the reader's curiosity and entice them to read the full article. Use UK spelling and grammar.

Your descriptions MUST be between 140-156 characters long.
"""

app = typer.Typer()


@app.command()
def describe(
    filepath: Annotations.filepath,
    model: Annotations.model = DEFAULT_AI_MODEL,
):
    """
    Send a blog post to ChatGPT to generate a one-line description. The result is copied to your clipboard.
    """
    Helpers.check_file_exists(filepath)
    Helpers.validate_model(model)

    user_content = filepath.read_text()

    with Helpers.get_spinner("Getting descriptions...") as progress:
        progress.add_task("")
        response = Helpers.query_gpt(
            model=model,
            messages=[
                {"role": "system", "content": DESCRIPTION_GENERATOR_CONTENT},
                {
                    "role": "user",
                    "content": f"Summarise this article: ```{user_content}```",
                },
            ],
            response_format=DescriptionResponse,
        )

    for i, description in enumerate(response.descriptions, start=1):
        print(f"[bold underline sky_blue1]Description {i}[/]\n{description}\n")

    selection = int(
        typer.prompt(
            f"Which description would you like to copy? ('{Helpers.none_selection}' for None)"
        )
    )

    pyperclip.copy(response.descriptions[selection - 1])
    print("[green]Copied to clipboard![/]")
