"""
Use Case: Renomear Tarefa.

Altera o título de uma tarefa existente.
"""

from dataclasses import dataclass

from app.application.common.errors import NotFoundError
from app.application.common.use_case import UseCase
from app.application.sample_context.ports import TaskRepositoryPort
from app.domain.sample_context.value_objects import TaskId, TaskTitle


@dataclass(frozen=True)
class RenameTaskInput:
    """Dados de entrada para renomear uma tarefa."""

    task_id: str
    new_title: str


@dataclass(frozen=True)
class RenameTaskOutput:
    """Dados de saída após renomear uma tarefa."""

    id: str
    old_title: str
    new_title: str


class RenameTaskUseCase(UseCase[RenameTaskInput, RenameTaskOutput]):
    """
    Use case para renomear uma tarefa.

    Busca a tarefa pelo ID e altera seu título.
    """

    def __init__(self, repository: TaskRepositoryPort) -> None:
        self._repository = repository

    def execute(self, input: RenameTaskInput) -> RenameTaskOutput:
        """
        Executa a renomeação da tarefa.

        Args:
            input: ID e novo título da tarefa

        Returns:
            Output com os títulos antigo e novo

        Raises:
            NotFoundError: Se a tarefa não existir
        """
        task_id = TaskId(input.task_id)
        task = self._repository.find_by_id(task_id)

        if task is None:
            raise NotFoundError("Task", input.task_id)

        old_title = task.title.value
        new_title = TaskTitle(input.new_title)

        task.rename(new_title)
        self._repository.save(task)

        return RenameTaskOutput(
            id=task.id.value,
            old_title=old_title,
            new_title=task.title.value,
        )
