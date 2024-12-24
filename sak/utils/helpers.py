import typer
from rich import print
from pathlib import Path
from rich.progress import Progress, SpinnerColumn, TextColumn
from pydantic import BaseModel
from openai import OpenAI

class ModelCost(BaseModel):
    cost: float
    per_amount: int


class GptModel(BaseModel):
    input: ModelCost
    output: ModelCost
    cached: ModelCost


MODELS = {
    "gpt-4o": GptModel(
        input=ModelCost(cost=2.50, per_amount=1_000_000),
        cached=ModelCost(cost=1.25, per_amount=1_000_000),
        output=ModelCost(cost=10.00, per_amount=1_000_000),
    ),
    "gpt-4o-mini": GptModel(
        input=ModelCost(cost=0.150, per_amount=1_000_000),
        cached=ModelCost(cost=0.075, per_amount=1_000_000),
        output=ModelCost(cost=0.600, per_amount=1_000_000),
    ),
}


def calc_cost(tokens: int, cost: float, per_amount: int):
    return tokens / per_amount * cost


class Helpers:
    @staticmethod
    def validate_model(model: str):
        if model not in MODELS.keys():
            print(f"[bold red]Error: '{model}' is not a valid model.")
            raise typer.Exit(code=1)

    @staticmethod
    def check_file_exists(filepath: Path):
        if not filepath.exists():
            print(f"[bold red]File not found:[/bold red] {filepath}")
            raise typer.Exit(code=1)

    @staticmethod
    def get_spinner(msg: str) -> Progress:
        return Progress(
            SpinnerColumn(style="purple3"),
            TextColumn(f"[bold purple3]{msg}"),
            transient=True,
        )

    none_selection = 0
    @staticmethod
    def isNoneSelection(choice: int):
        if choice == Helpers.none_selection:
            print("Nothing copied.")
            raise typer.Exit()

    @staticmethod
    def query_gpt(model: str, messages: list, response_format: BaseModel):
        try:
            client = OpenAI()
            completion = client.beta.chat.completions.parse(
                model=model,
                messages=messages,
                response_format=response_format,
            )
            message = completion.choices[0].message

            model_pricing = MODELS[model]

            style = "yellow"
            print(f"[{style}]-----------Usage Stats-----------[/]")
            print(f"[{style}]Model: [/] {completion.model}")

            prompt_cost = calc_cost(
                completion.usage.prompt_tokens,
                model_pricing.input.cost,
                model_pricing.input.per_amount,
            )
            print(f"[{style}]Prompt Tokens:[/] {completion.usage.prompt_tokens}")

            completion_cost = calc_cost(
                completion.usage.completion_tokens,
                model_pricing.output.cost,
                model_pricing.output.per_amount,
            )
            print(
                f"[{style}]Completion Tokens:[/] {completion.usage.completion_tokens}"
            )

            print(f"[{style}]Total Tokens: [/] {completion.usage.total_tokens}")
            print(f"[{style}]Total Cost: [/] ${prompt_cost + completion_cost}")
            print(f"[{style}]---------------------------------[/]")

            if message.parsed:
                return message.parsed
            elif message.refusal:
                print(message.refusal)
                raise typer.Exit(code=1)
        except Exception as e:
            print(e)
            raise typer.Exit(code=1)