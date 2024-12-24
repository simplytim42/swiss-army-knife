import typer
from pydantic import BaseModel
from rich import print
from ..utils import DEFAULT_AI_MODEL, Annotations, Helpers

class ReviewTask(BaseModel):
    rating: int
    comments: str


class ReviewResponse(BaseModel):
    correctness: ReviewTask
    clarity: ReviewTask
    accuracy: ReviewTask
    structure: ReviewTask
    consistency: ReviewTask
    readability: ReviewTask
    story: ReviewTask


POST_REVIEWER_CONTENT = """
You are a skilled, concise proofreader specialising in technical blog posts.
Articles provided within triple backticks are in markdown format (for 'Material for MKDocs') and may include front matter you can ignore.

Your tasks for each article:
1. **Correctness:** Rate spelling/grammar accuracy (UK English).
2. **Clarity:** Rate how clearly complex ideas are explained.
3. **Accuracy:** Verify technical accuracy (facts, code snippets).
4. **Structure:** Check for logical flow, clear headings, smooth transitions.
5. **Consistency:** Ensure consistent tone, terminology, and formatting.
6. **Readability:** Identify any overly complex sentences; suggest lists where helpful.
7. **Story:** Check if any 'setup, conflict, resolution' structure would enhance flow.

Rate each task out of 5.

**Only comment on tasks rated below 5/5 if you identify a significant improvement.**
**Comments must be explicitly related to the text to enable the errors to be found.**
**Generic or Minor feedback should not be commented on.**
**If the rating for a task is 5/5, then just provide the comment 'No comment'.**
"""

app = typer.Typer()


@app.command()
def review(
    filepath: Annotations.filepath,
    model: Annotations.model = DEFAULT_AI_MODEL,
):
    """
    Send a blog post to ChatGPT for review.
    """
    Helpers.check_file_exists(filepath)
    Helpers.validate_model(model)

    user_content = filepath.read_text()

    with Helpers.get_spinner("Reviewing blog post...") as progress:
        progress.add_task("")
        response = Helpers.query_gpt(
            model=model,
            messages=[
                {"role": "system", "content": POST_REVIEWER_CONTENT},
                {
                    "role": "user",
                    "content": f"Analyse this article: ```{user_content}```",
                },
            ],
            response_format=ReviewResponse,
        )

    for field, value in response:
        print(f"[bold underline sky_blue1]{field.title()}[/]: {value.rating}/5")
        print(value.comments.strip() + "\n")
