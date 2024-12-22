import typer
from openai import OpenAI
from rich import print
import json
import pyperclip
from ..utils import DEFAULT_AI_MODEL, Annotations, Helpers

DESCRIPTION_GENERATOR_CONTENT = """
You are a skilled, concise summariser specialising in technical blog posts and SEO. Articles provided within triple backticks are in markdown format (for 'Material for MKDocs') and may include front matter you can ignore.

Your task is to create **three distinct one-line summaries** that will pique the reader's curiosity and entice them to read the full article. Use UK spelling and grammar.

Your descriptions MUST be between 140-156 characters long.

**Respond ONLY with a JSON array of strings, formatted as follows:**
[
    "First summary",
    "Second summary",
    "Third summary"
]
**Do not include any additional commentary or formatting outside of the JSON array.**
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
    client = OpenAI()

    with Helpers.get_spinner("Getting descriptions...") as progress:
        progress.add_task("")
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": DESCRIPTION_GENERATOR_CONTENT},
                {
                    "role": "user",
                    "content": f"Summarise this article: ```{user_content}```",
                },
            ],
        )

    try:
        descriptions = json.loads(completion.choices[0].message.content)
    except json.JSONDecodeError:
        print("[red]Response was not in JSON format...")
        raise typer.Abort()

    for i, description in enumerate(descriptions, start=1):
        print(f"[bold underline sky_blue1]Description {i}[/]\n{description}\n")

    selection = int(typer.prompt("Which description would you like to copy?"))

    pyperclip.copy(descriptions[selection - 1])
    print("[green]Copied to clipboard![/]")
