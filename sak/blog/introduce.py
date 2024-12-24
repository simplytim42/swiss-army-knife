import typer
from rich import print
import pyperclip
from ..utils import DEFAULT_AI_MODEL, Annotations, Helpers
from pydantic import BaseModel


class IntroResponse(BaseModel):
    excerpts: list[str]

EXCERPT_GENERATOR_CONTENT = """
You are a skilled content summariser specialising in technical blog posts. Articles provided within triple backticks are in markdown format (for 'Material for MKDocs') and may include front matter you can ignore.

Your task is to craft **three distinct one-paragraph excerpts** that effectively introduce the article's main ideas, setting the stage for readers and sparking their interest to continue reading.
Be concise and casual.
Refer to the reader in the second person (you).
Do not refer to the title of the article.
Use UK spelling and grammar.
"""

app = typer.Typer()


@app.command()
def introduce(
    filepath: Annotations.filepath,
    model: Annotations.model = DEFAULT_AI_MODEL,
):
    """
    Send a blog post to ChatGPT to generate an introduction.
    """
    Helpers.check_file_exists(filepath)
    Helpers.validate_model(model)

    user_content = filepath.read_text()

    with Helpers.get_spinner("Preparing introductions...") as progress:
        progress.add_task("")
        response = Helpers.query_gpt(
            model=model,
            messages=[
                {"role": "system", "content": EXCERPT_GENERATOR_CONTENT},
                {
                    "role": "user",
                    "content": f"Introduce this article: ```{user_content}```",
                },
            ],
            response_format=IntroResponse,
        )

    for i, excerpt in enumerate(response.excerpts, start=1):
        print(f"[bold underline dark_orange]Excerpt {i}[/]\n{excerpt}\n")

    selection = int(
        typer.prompt(
            f"Which except would you like to copy? ('{Helpers.none_selection}' for None)"
        )
    )

    Helpers.isNoneSelection(selection)

    pyperclip.copy(response.excerpts[selection - 1])
    print("[green]Copied to clipboard![/]")
