import typer
from openai import OpenAI
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
import json
import pyperclip
from ..utils.config import DEFAULT_AI_MODEL
from ..utils.helpers import validate_model
from ..utils.annotations import Annotations

TITLE_GENERATOR_CONTENT = """
You are a skilled, concise summariser specialising in technical blog posts and SEO. Articles provided within triple backticks are in markdown format (for 'Material for MKDocs') and may include front matter you can ignore.

Your task is to create **three distinct one-line titles** that will pique the reader's curiosity and entice them to read the full article. Use UK spelling and grammar.

Your titles MUST be between 40 and 50 characters.

**Respond ONLY with a JSON array of strings, formatted as follows:**
[
    "First title",
    "Second title",
    "Third title"
]
**Do not include any additional commentary or formatting outside of the JSON array.**
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
    if not filepath.exists():
        print(f"[bold red]File not found:[/bold red] {filepath}")
        raise typer.Exit(code=1)

    validate_model(model)

    user_content = filepath.open().read()
    client = OpenAI()

    with Progress(
        SpinnerColumn(style="purple3"),
        TextColumn("[bold purple3]Generating titles..."),
        transient=True,
    ) as progress:
        progress.add_task("")
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": TITLE_GENERATOR_CONTENT},
                {
                    "role": "user",
                    "content": f"Create a title this article: ```{user_content}```",
                },
            ],
        )

    try:
        titles = json.loads(completion.choices[0].message.content)
    except json.JSONDecodeError:
        print("Response was not in JSON format...")
        raise typer.Abort()

    for i, title in enumerate(titles, start=1):
        print(f"[bold underline sky_blue1]Title {i}[/]\n{title}\n")

    selection = int(
        typer.prompt("Which title would you like to copy to your clipboard?")
    )

    pyperclip.copy(titles[selection - 1])
