"""
CLI para gerenciamento de tarefas.

Interface de linha de comando que utiliza o Composition Root
para obter use cases já configurados com suas dependências.

A CLI NÃO instancia dependências diretamente - usa o container.
Isso garante consistência e facilita testes.
"""

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from app.application.common.errors import NotFoundError
from app.application.sample_context.use_cases.complete_task import CompleteTaskInput
from app.application.sample_context.use_cases.create_task import CreateTaskInput
from app.application.sample_context.use_cases.list_tasks import ListTasksInput, TaskFilter
from app.application.sample_context.use_cases.rename_task import RenameTaskInput
from app.bootstrap import Container, get_container
from app.domain.common.exceptions import DomainException, ValidationException


app = typer.Typer(
    name="task-cli",
    help="CLI para gerenciamento de tarefas - DDD Enterprise Template",
    add_completion=False,
)
console = Console()


def get_cli_container() -> Container:
    """
    Obtém o container de dependências para a CLI.

    Centraliza a obtenção do container, facilitando testes.
    """
    return get_container()


@app.command("create")
def create_task(
    title: Annotated[str, typer.Argument(help="Título da tarefa")],
    priority: Annotated[
        str, typer.Option("--priority", "-p", help="Prioridade: low, medium, high, urgent")
    ] = "medium",
    description: Annotated[
        str, typer.Option("--description", "-d", help="Descrição da tarefa")
    ] = "",
) -> None:
    """Cria uma nova tarefa."""
    container = get_cli_container()

    try:
        output = container.create_task_use_case.execute(
            CreateTaskInput(
                title=title,
                priority=priority,
                description=description,
            )
        )

        console.print("[green]✓ Tarefa criada com sucesso![/green]")
        console.print(f"  ID: {output.id}")
        console.print(f"  Título: {output.title}")
        console.print(f"  Prioridade: {output.priority}")
        console.print(f"  Status: {output.status}")

    except ValidationException as e:
        console.print(f"[red]✗ Erro de validação: {e.message}[/red]")
        raise typer.Exit(1)
    except DomainException as e:
        console.print(f"[red]✗ Erro: {e.message}[/red]")
        raise typer.Exit(1)


@app.command("list")
def list_tasks(
    filter_status: Annotated[
        str, typer.Option("--filter", "-f", help="Filtro: all, pending, completed")
    ] = "all",
) -> None:
    """Lista todas as tarefas."""
    container = get_cli_container()

    try:
        task_filter = TaskFilter(filter_status)
    except ValueError:
        console.print("[red]✗ Filtro inválido. Use: all, pending, completed[/red]")
        raise typer.Exit(1)

    output = container.list_tasks_use_case.execute(ListTasksInput(filter=task_filter))

    if output.total == 0:
        console.print("[yellow]Nenhuma tarefa encontrada.[/yellow]")
        return

    table = Table(title=f"Tarefas ({output.total})")
    table.add_column("ID", style="dim")
    table.add_column("Título")
    table.add_column("Prioridade")
    table.add_column("Status")
    table.add_column("Criada em")

    for task in output.tasks:
        priority_color = {
            "low": "blue",
            "medium": "white",
            "high": "yellow",
            "urgent": "red",
        }.get(task.priority, "white")

        status_color = {
            "pending": "yellow",
            "in_progress": "blue",
            "completed": "green",
            "cancelled": "red",
        }.get(task.status, "white")

        table.add_row(
            task.id[:8] + "...",
            task.title,
            f"[{priority_color}]{task.priority}[/{priority_color}]",
            f"[{status_color}]{task.status}[/{status_color}]",
            task.created_at[:10],
        )

    console.print(table)


@app.command("complete")
def complete_task(
    task_id: Annotated[str, typer.Argument(help="ID da tarefa")],
) -> None:
    """Marca uma tarefa como concluída."""
    container = get_cli_container()

    try:
        output = container.complete_task_use_case.execute(
            CompleteTaskInput(task_id=task_id)
        )

        console.print("[green]✓ Tarefa concluída![/green]")
        console.print(f"  Título: {output.title}")
        console.print(f"  Concluída em: {output.completed_at}")

    except NotFoundError as e:
        console.print(f"[red]✗ {e.message}[/red]")
        raise typer.Exit(1)
    except DomainException as e:
        console.print(f"[red]✗ Erro: {e.message}[/red]")
        raise typer.Exit(1)


@app.command("rename")
def rename_task(
    task_id: Annotated[str, typer.Argument(help="ID da tarefa")],
    new_title: Annotated[str, typer.Argument(help="Novo título")],
) -> None:
    """Renomeia uma tarefa."""
    container = get_cli_container()

    try:
        output = container.rename_task_use_case.execute(
            RenameTaskInput(
                task_id=task_id,
                new_title=new_title,
            )
        )

        console.print("[green]✓ Tarefa renomeada![/green]")
        console.print(f"  De: {output.old_title}")
        console.print(f"  Para: {output.new_title}")

    except NotFoundError as e:
        console.print(f"[red]✗ {e.message}[/red]")
        raise typer.Exit(1)
    except ValidationException as e:
        console.print(f"[red]✗ Erro de validação: {e.message}[/red]")
        raise typer.Exit(1)
    except DomainException as e:
        console.print(f"[red]✗ Erro: {e.message}[/red]")
        raise typer.Exit(1)


@app.command("demo")
def demo() -> None:
    """Executa uma demonstração criando algumas tarefas."""
    container = get_cli_container()

    console.print("[bold blue]🚀 Executando demonstração do DDD Enterprise Template[/bold blue]\n")

    # Criar algumas tarefas de exemplo
    tasks_data = [
        ("Estudar Domain-Driven Design", "high", "Ler o livro azul do Eric Evans"),
        ("Configurar ambiente de desenvolvimento", "urgent", ""),
        ("Escrever testes unitários", "medium", "Cobrir pelo menos 85% do código"),
        ("Revisar pull request", "low", ""),
    ]

    created_ids: list[str] = []

    console.print("[bold]Criando tarefas de exemplo...[/bold]")
    for title, priority, description in tasks_data:
        output = container.create_task_use_case.execute(
            CreateTaskInput(title=title, priority=priority, description=description)
        )
        created_ids.append(output.id)
        console.print(f"  [green]✓[/green] {title}")

    console.print()

    # Completar uma tarefa
    if created_ids:
        console.print("[bold]Completando uma tarefa...[/bold]")
        container.complete_task_use_case.execute(
            CompleteTaskInput(task_id=created_ids[1])
        )
        console.print("  [green]✓[/green] Tarefa completada\n")

    # Listar todas as tarefas
    console.print("[bold]Listando todas as tarefas:[/bold]")
    list_tasks()


if __name__ == "__main__":
    app()
