import typer
from .review import app as review_app
from .describe import app as describe_app
from .title import app as title_app
from .introduce import app as introduce_app
from .publish import app as publish_app

app = typer.Typer(no_args_is_help=True, help="Manage blog posts.")

app.add_typer(review_app)
app.add_typer(describe_app)
app.add_typer(title_app)
app.add_typer(introduce_app)
app.add_typer(publish_app)
