"""
Task - Entidade principal do sample context.

Representa uma tarefa no sistema de gerenciamento de tarefas.
"""

from datetime import datetime

from app.domain.common.entity import Entity
from app.domain.common.exceptions import BusinessRuleViolationException
from app.domain.sample_context.events.task_events import (
    TaskCancelled,
    TaskCompleted,
    TaskCreated,
    TaskPriorityChanged,
    TaskRenamed,
)
from app.domain.sample_context.value_objects import (
    TaskDescription,
    TaskId,
    TaskPriority,
    TaskStatus,
    TaskTitle,
)
from app.domain.sample_context.value_objects.task_status import StatusValue


class Task(Entity[TaskId]):
    """
    Entidade Task - representa uma tarefa no sistema.

    Regras de negócio:
    - Uma tarefa concluída não pode ser modificada
    - Uma tarefa cancelada não pode ser reaberta
    - Apenas tarefas pendentes ou em progresso podem ser concluídas
    """

    __slots__ = (
        "_title",
        "_description",
        "_priority",
        "_status",
        "_created_at",
        "_completed_at",
    )

    def __init__(
        self,
        id: TaskId,
        title: TaskTitle,
        description: TaskDescription,
        priority: TaskPriority,
        status: TaskStatus,
        created_at: datetime,
        completed_at: datetime | None = None,
    ) -> None:
        """
        Inicializa uma Task.

        Use os factory methods create() para criar novas tarefas.
        """
        super().__init__(id)
        self._title = title
        self._description = description
        self._priority = priority
        self._status = status
        self._created_at = created_at
        self._completed_at = completed_at

    @classmethod
    def create(
        cls,
        id: TaskId,
        title: TaskTitle,
        priority: TaskPriority,
        created_at: datetime,
        description: TaskDescription | None = None,
    ) -> "Task":
        """
        Factory method para criar uma nova tarefa.

        Args:
            id: Identificador único
            title: Título da tarefa
            priority: Prioridade da tarefa
            created_at: Data/hora de criação
            description: Descrição opcional

        Returns:
            Nova instância de Task
        """
        task = cls(
            id=id,
            title=title,
            description=description or TaskDescription.empty(),
            priority=priority,
            status=TaskStatus.pending(),
            created_at=created_at,
        )

        task.add_event(
            TaskCreated(
                task_id=id.value,
                title=title.value,
                priority=priority.value,
            )
        )

        return task

    @property
    def title(self) -> TaskTitle:
        """Retorna o título da tarefa."""
        return self._title

    @property
    def description(self) -> TaskDescription:
        """Retorna a descrição da tarefa."""
        return self._description

    @property
    def priority(self) -> TaskPriority:
        """Retorna a prioridade da tarefa."""
        return self._priority

    @property
    def status(self) -> TaskStatus:
        """Retorna o status da tarefa."""
        return self._status

    @property
    def created_at(self) -> datetime:
        """Retorna a data de criação."""
        return self._created_at

    @property
    def completed_at(self) -> datetime | None:
        """Retorna a data de conclusão, se houver."""
        return self._completed_at

    @property
    def is_completed(self) -> bool:
        """Retorna True se a tarefa foi concluída."""
        return self._status.is_completed

    @property
    def is_open(self) -> bool:
        """Retorna True se a tarefa ainda está aberta."""
        return self._status.is_open

    def rename(self, new_title: TaskTitle) -> None:
        """
        Altera o título da tarefa.

        Args:
            new_title: Novo título

        Raises:
            BusinessRuleViolationException: Se a tarefa não puder ser modificada
        """
        self._ensure_can_modify()

        if self._title == new_title:
            return

        old_title = self._title
        self._title = new_title

        self.add_event(
            TaskRenamed(
                task_id=self.id.value,
                old_title=old_title.value,
                new_title=new_title.value,
            )
        )

    def change_description(self, new_description: TaskDescription) -> None:
        """
        Altera a descrição da tarefa.

        Args:
            new_description: Nova descrição

        Raises:
            BusinessRuleViolationException: Se a tarefa não puder ser modificada
        """
        self._ensure_can_modify()
        self._description = new_description

    def change_priority(self, new_priority: TaskPriority) -> None:
        """
        Altera a prioridade da tarefa.

        Args:
            new_priority: Nova prioridade

        Raises:
            BusinessRuleViolationException: Se a tarefa não puder ser modificada
        """
        self._ensure_can_modify()

        if self._priority == new_priority:
            return

        old_priority = self._priority
        self._priority = new_priority

        self.add_event(
            TaskPriorityChanged(
                task_id=self.id.value,
                old_priority=old_priority.value,
                new_priority=new_priority.value,
            )
        )

    def start(self) -> None:
        """
        Inicia a tarefa (muda para in_progress).

        Raises:
            BusinessRuleViolationException: Se a tarefa não estiver pendente
        """
        if self._status.status != StatusValue.PENDING:
            raise BusinessRuleViolationException(
                rule="TaskCanOnlyStartWhenPending",
                message="Apenas tarefas pendentes podem ser iniciadas.",
            )

        self._status = TaskStatus.in_progress()

    def complete(self, completed_at: datetime) -> None:
        """
        Marca a tarefa como concluída.

        Args:
            completed_at: Data/hora de conclusão

        Raises:
            BusinessRuleViolationException: Se a tarefa não puder ser concluída
        """
        if not self._status.is_open:
            raise BusinessRuleViolationException(
                rule="TaskCanOnlyCompleteWhenOpen",
                message="Apenas tarefas abertas podem ser concluídas.",
            )

        self._status = TaskStatus.completed()
        self._completed_at = completed_at

        self.add_event(
            TaskCompleted(
                task_id=self.id.value,
                title=self._title.value,
            )
        )

    def cancel(self) -> None:
        """
        Cancela a tarefa.

        Raises:
            BusinessRuleViolationException: Se a tarefa já estiver finalizada
        """
        if not self._status.is_open:
            raise BusinessRuleViolationException(
                rule="TaskCanOnlyCancelWhenOpen",
                message="Apenas tarefas abertas podem ser canceladas.",
            )

        self._status = TaskStatus.cancelled()

        self.add_event(
            TaskCancelled(
                task_id=self.id.value,
                title=self._title.value,
            )
        )

    def _ensure_can_modify(self) -> None:
        """Verifica se a tarefa pode ser modificada."""
        if not self._status.is_open:
            raise BusinessRuleViolationException(
                rule="TaskCanOnlyModifyWhenOpen",
                message="Tarefas finalizadas não podem ser modificadas.",
            )

    def __repr__(self) -> str:
        return (
            f"Task(id={self.id.value!r}, title={self._title.value!r}, "
            f"status={self._status.value!r})"
        )
