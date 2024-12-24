import typer
from rich import print
import pyperclip
from ..utils import DEFAULT_AI_MODEL, Helpers, Annotations
from pydantic import BaseModel


class TitleResponse(BaseModel):
    titles: list[str]


TITLE_GENERATOR_CONTENT = """
You are a skilled, concise summariser specialising in technical blog posts and SEO. Articles provided within triple backticks are in markdown format (for 'Material for MKDocs') and may include front matter you can ignore.

Your task is to create **three distinct one-line titles** that will pique the reader's curiosity and entice them to read the full article. Use UK spelling and grammar.

Your titles MUST be between 30 and 50 characters.
"""

app = typer.Typer()


@app.command()
def title(
    filepath: Annotations.filepath,
    model: Annotations.model = DEFAULT_AI_MODEL,
):
    """
    Send a blog post to ChatGPT to generate a title. The result is copied to your clipboard.
    """
    Helpers.check_file_exists(filepath)
    Helpers.validate_model(model)

    user_content = filepath.read_text()

    with Helpers.get_spinner("Generating titles...") as progress:
        progress.add_task("")

        response = Helpers.query_gpt(
            model=model,
            messages=[
                {"role": "system", "content": TITLE_GENERATOR_CONTENT},
                {
                    "role": "user",
                    "content": f"Create a title this article: ```{user_content}```",
                },
            ],
            response_format=TitleResponse,
        )

    for i, title in enumerate(response.titles, start=1):
        print(f"[bold underline sky_blue1]Title {i}[/]\n{title}\n")

    selection = int(
        typer.prompt(
            f"Which title would you like to copy? ('{Helpers.none_selection}' for None)"
        )
    )

    Helpers.isNoneSelection(selection)

    pyperclip.copy(response.titles[selection - 1])
    print("[green]Copied to clipboard![/]")
