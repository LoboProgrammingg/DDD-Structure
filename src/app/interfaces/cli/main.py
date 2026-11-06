"""CLI: segundo adaptador de entrada sobre os mesmos casos de uso da API.

task-cli create "Revisar ADRs" --priority high
task-cli list --status pending
"""

import asyncio
from collections.abc import Awaitable, Callable
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from app.application.shared import ApplicationError
from app.application.task_management.commands import (
    AssignTask,
    CompleteTask,
    CreateTask,
    StartTask,
)
from app.application.task_management.queries import ListTasks
from app.bootstrap import Container, build_container
from app.domain.seedwork import DomainError
from app.domain.task_management.value_objects import TaskStatus

app = typer.Typer(help="Gerencie tarefas pela linha de comando.", no_args_is_help=True)
console = Console()


def _run[T](operation: Callable[[Container], Awaitable[T]]) -> T:
    async def runner() -> T:
        container = build_container()
        try:
            return await operation(container)
        finally:
            await container.dispose()

    try:
        return asyncio.run(runner())
    except (DomainError, ApplicationError) as error:
        console.print(f"[red]Erro:[/red] {error.message}")
        raise typer.Exit(code=1) from error


@app.command()
def create(
    title: str,
    priority: Annotated[str, typer.Option(help="low, medium, high ou urgent")] = "medium",
) -> None:
    """Cria uma tarefa."""
    task_id = _run(lambda c: c.create_task(CreateTask(title=title, priority=priority)))
    console.print(f"[green]Tarefa criada:[/green] {task_id}")


@app.command("list")
def list_tasks(
    status: Annotated[TaskStatus | None, typer.Option(help="Filtra pelo status")] = None,
) -> None:
    """Lista as tarefas."""
    page = _run(lambda c: c.list_tasks(ListTasks(status=status)))
    table = Table("ID", "Título", "Prioridade", "Status", "Responsável")
    for task in page.items:
        table.add_row(task.id, task.title, task.priority, task.status, task.assignee_id or "-")
    console.print(table)
    console.print(f"{page.total} tarefa(s)")


@app.command()
def assign(task_id: str, assignee_id: str) -> None:
    """Define o responsável por uma tarefa."""
    _run(lambda c: c.assign_task(AssignTask(task_id=task_id, assignee_id=assignee_id)))
    console.print("[green]Responsável definido.[/green]")


@app.command()
def start(task_id: str) -> None:
    """Inicia uma tarefa respeitando o limite de WIP."""
    _run(lambda c: c.start_task(StartTask(task_id=task_id)))
    console.print("[green]Tarefa iniciada.[/green]")


@app.command()
def complete(task_id: str) -> None:
    """Conclui uma tarefa."""
    _run(lambda c: c.complete_task(CompleteTask(task_id=task_id)))
    console.print("[green]Tarefa concluída.[/green]")


if __name__ == "__main__":
    app()
