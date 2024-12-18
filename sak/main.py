import typer
from .version import app as version_app
from .blog import app as blog_app

OVERVIEW = """
Swiss Army Knife (sak).

The following environment variables need to exist:\n\n- OPENAI_API_KEY\n\n- MEDIUM_API_KEY\n\n- DEV_API_KEY
"""

app = typer.Typer(no_args_is_help=True, help=OVERVIEW)

app.add_typer(version_app)
app.add_typer(blog_app, name="blog")
