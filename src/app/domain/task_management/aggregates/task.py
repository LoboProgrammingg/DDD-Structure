"""Agregado Task: a raiz protege todas as invariantes do ciclo de vida da tarefa."""

from datetime import datetime

from app.domain.seedwork import AggregateRoot
from app.domain.task_management.events import (
    TaskAssigned,
    TaskCancelled,
    TaskCompleted,
    TaskCreated,
    TaskPriorityChanged,
    TaskRenamed,
    TaskStarted,
)
from app.domain.task_management.exceptions import (
    DueDateBeforeCreation,
    InvalidStatusTransition,
    TaskIsClosed,
    TaskNotAssigned,
)
from app.domain.task_management.value_objects import (
    AssigneeId,
    DueDate,
    TaskDescription,
    TaskId,
    TaskPriority,
    TaskStatus,
    TaskTitle,
)


class Task(AggregateRoot[TaskId]):
    """Tarefa de trabalho.

    Invariantes:
    * tarefas encerradas (concluídas ou canceladas) não podem ser alteradas;
    * o status só muda pelas transições permitidas em ``TaskStatus``;
    * só tarefas com responsável podem ser iniciadas;
    * o prazo não pode ser anterior à data de criação.

    O construtor apenas reconstitui o estado (usado pelo repositório).
    Novas tarefas nascem pela factory ``Task.create``.
    """

    def __init__(
        self,
        task_id: TaskId,
        *,
        title: TaskTitle,
        description: TaskDescription,
        priority: TaskPriority,
        status: TaskStatus,
        created_at: datetime,
        due_date: DueDate | None = None,
        assignee_id: AssigneeId | None = None,
        completed_at: datetime | None = None,
        version: int = 0,
    ) -> None:
        super().__init__(task_id, version)
        self._title = title
        self._description = description
        self._priority = priority
        self._status = status
        self._created_at = created_at
        self._due_date = due_date
        self._assignee_id = assignee_id
        self._completed_at = completed_at

    @classmethod
    def create(
        cls,
        task_id: TaskId,
        *,
        title: TaskTitle,
        priority: TaskPriority,
        created_at: datetime,
        description: TaskDescription | None = None,
        due_date: DueDate | None = None,
    ) -> "Task":
        if due_date is not None and due_date.is_before(created_at):
            raise DueDateBeforeCreation("O prazo não pode ser anterior à criação da tarefa.")

        task = cls(
            task_id,
            title=title,
            description=description or TaskDescription(),
            priority=priority,
            status=TaskStatus.PENDING,
            created_at=created_at,
            due_date=due_date,
        )
        task._record(TaskCreated(task_id=str(task_id), title=title.value, priority=priority.value))
        return task

    @property
    def title(self) -> TaskTitle:
        return self._title

    @property
    def description(self) -> TaskDescription:
        return self._description

    @property
    def priority(self) -> TaskPriority:
        return self._priority

    @property
    def status(self) -> TaskStatus:
        return self._status

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def due_date(self) -> DueDate | None:
        return self._due_date

    @property
    def assignee_id(self) -> AssigneeId | None:
        return self._assignee_id

    @property
    def completed_at(self) -> datetime | None:
        return self._completed_at

    def is_overdue(self, at: datetime) -> bool:
        return self._status.is_open and self._due_date is not None and self._due_date.is_before(at)

    def rename(self, title: TaskTitle) -> None:
        self._ensure_open()
        if title == self._title:
            return
        previous, self._title = self._title, title
        self._record(
            TaskRenamed(task_id=str(self.id), previous_title=previous.value, new_title=title.value)
        )

    def describe(self, description: TaskDescription) -> None:
        self._ensure_open()
        self._description = description

    def reprioritize(self, priority: TaskPriority) -> None:
        self._ensure_open()
        if priority == self._priority:
            return
        previous, self._priority = self._priority, priority
        self._record(
            TaskPriorityChanged(
                task_id=str(self.id),
                previous_priority=previous.value,
                new_priority=priority.value,
            )
        )

    def assign_to(self, assignee_id: AssigneeId) -> None:
        self._ensure_open()
        if assignee_id == self._assignee_id:
            return
        self._assignee_id = assignee_id
        self._record(
            TaskAssigned(
                task_id=str(self.id), title=self._title.value, assignee_id=assignee_id.value
            )
        )

    def start(self) -> None:
        """Prefira ``WorkInProgressPolicy.start``, que também aplica o limite de WIP."""
        if self._assignee_id is None:
            raise TaskNotAssigned("A tarefa precisa de um responsável para ser iniciada.")
        self._transition_to(TaskStatus.IN_PROGRESS)
        self._record(TaskStarted(task_id=str(self.id), assignee_id=self._assignee_id.value))

    def complete(self, at: datetime) -> None:
        self._transition_to(TaskStatus.COMPLETED)
        self._completed_at = at
        self._record(TaskCompleted(task_id=str(self.id), title=self._title.value))

    def cancel(self) -> None:
        self._transition_to(TaskStatus.CANCELLED)
        self._record(TaskCancelled(task_id=str(self.id), title=self._title.value))

    def _transition_to(self, target: TaskStatus) -> None:
        if not self._status.can_transition_to(target):
            raise InvalidStatusTransition(
                f"Não é possível mudar a tarefa de '{self._status}' para '{target}'."
            )
        self._status = target

    def _ensure_open(self) -> None:
        if not self._status.is_open:
            raise TaskIsClosed(f"A tarefa está '{self._status}' e não pode ser alterada.")
