"""
Testes unitários para a entidade Task.
"""

from datetime import UTC, datetime

import pytest

from app.domain.common.exceptions import BusinessRuleViolationException
from app.domain.sample_context.entities.task import Task
from app.domain.sample_context.events.task_events import (
    TaskCompleted,
    TaskCreated,
    TaskRenamed,
)
from app.domain.sample_context.value_objects import (
    TaskDescription,
    TaskId,
    TaskPriority,
    TaskTitle,
)


class TestTaskCreation:
    """Testes para criação de Task."""

    @pytest.mark.unit
    def test_create_task_with_factory_method(self) -> None:
        # Arrange
        task_id = TaskId("task-001")
        title = TaskTitle("Minha tarefa")
        priority = TaskPriority.high()
        created_at = datetime(2024, 1, 15, 10, 0, 0, tzinfo=UTC)

        # Act
        task = Task.create(
            id=task_id,
            title=title,
            priority=priority,
            created_at=created_at,
        )

        # Assert
        assert task.id == task_id
        assert task.title == title
        assert task.priority == priority
        assert task.status.value == "pending"
        assert task.created_at == created_at
        assert task.completed_at is None
        assert task.description.is_empty

    @pytest.mark.unit
    def test_create_task_with_description(self) -> None:
        # Arrange
        description = TaskDescription("Uma descrição detalhada")

        # Act
        task = Task.create(
            id=TaskId("task-001"),
            title=TaskTitle("Tarefa"),
            priority=TaskPriority.medium(),
            created_at=datetime.now(UTC),
            description=description,
        )

        # Assert
        assert task.description == description
        assert not task.description.is_empty

    @pytest.mark.unit
    def test_create_task_emits_task_created_event(self) -> None:
        # Arrange & Act
        task = Task.create(
            id=TaskId("task-001"),
            title=TaskTitle("Tarefa"),
            priority=TaskPriority.medium(),
            created_at=datetime.now(UTC),
        )

        # Assert
        events = task.domain_events
        assert len(events) == 1
        assert isinstance(events[0], TaskCreated)
        assert events[0].task_id == "task-001"
        assert events[0].title == "Tarefa"


class TestTaskRename:
    """Testes para renomeação de Task."""

    @pytest.mark.unit
    def test_rename_task(self) -> None:
        # Arrange
        task = Task.create(
            id=TaskId("task-001"),
            title=TaskTitle("Título original"),
            priority=TaskPriority.medium(),
            created_at=datetime.now(UTC),
        )
        task.clear_events()  # Limpa evento de criação

        # Act
        task.rename(TaskTitle("Novo título"))

        # Assert
        assert task.title.value == "Novo título"

    @pytest.mark.unit
    def test_rename_task_emits_event(self) -> None:
        # Arrange
        task = Task.create(
            id=TaskId("task-001"),
            title=TaskTitle("Título original"),
            priority=TaskPriority.medium(),
            created_at=datetime.now(UTC),
        )
        task.clear_events()

        # Act
        task.rename(TaskTitle("Novo título"))

        # Assert
        events = task.domain_events
        assert len(events) == 1
        assert isinstance(events[0], TaskRenamed)
        assert events[0].old_title == "Título original"
        assert events[0].new_title == "Novo título"

    @pytest.mark.unit
    def test_rename_with_same_title_does_not_emit_event(self) -> None:
        # Arrange
        task = Task.create(
            id=TaskId("task-001"),
            title=TaskTitle("Título"),
            priority=TaskPriority.medium(),
            created_at=datetime.now(UTC),
        )
        task.clear_events()

        # Act
        task.rename(TaskTitle("Título"))

        # Assert
        assert len(task.domain_events) == 0

    @pytest.mark.unit
    def test_cannot_rename_completed_task(self) -> None:
        # Arrange
        task = Task.create(
            id=TaskId("task-001"),
            title=TaskTitle("Tarefa"),
            priority=TaskPriority.medium(),
            created_at=datetime.now(UTC),
        )
        task.complete(datetime.now(UTC))

        # Act & Assert
        with pytest.raises(BusinessRuleViolationException) as exc_info:
            task.rename(TaskTitle("Novo título"))

        assert "finalizadas" in exc_info.value.message.lower()


class TestTaskComplete:
    """Testes para conclusão de Task."""

    @pytest.mark.unit
    def test_complete_task(self) -> None:
        # Arrange
        task = Task.create(
            id=TaskId("task-001"),
            title=TaskTitle("Tarefa"),
            priority=TaskPriority.medium(),
            created_at=datetime.now(UTC),
        )
        completed_at = datetime(2024, 1, 20, 15, 0, 0, tzinfo=UTC)

        # Act
        task.complete(completed_at)

        # Assert
        assert task.is_completed
        assert task.completed_at == completed_at
        assert not task.is_open

    @pytest.mark.unit
    def test_complete_task_emits_event(self) -> None:
        # Arrange
        task = Task.create(
            id=TaskId("task-001"),
            title=TaskTitle("Tarefa"),
            priority=TaskPriority.medium(),
            created_at=datetime.now(UTC),
        )
        task.clear_events()

        # Act
        task.complete(datetime.now(UTC))

        # Assert
        events = task.domain_events
        assert len(events) == 1
        assert isinstance(events[0], TaskCompleted)
        assert events[0].task_id == "task-001"

    @pytest.mark.unit
    def test_cannot_complete_already_completed_task(self) -> None:
        # Arrange
        task = Task.create(
            id=TaskId("task-001"),
            title=TaskTitle("Tarefa"),
            priority=TaskPriority.medium(),
            created_at=datetime.now(UTC),
        )
        task.complete(datetime.now(UTC))

        # Act & Assert
        with pytest.raises(BusinessRuleViolationException):
            task.complete(datetime.now(UTC))

    @pytest.mark.unit
    def test_cannot_complete_cancelled_task(self) -> None:
        # Arrange
        task = Task.create(
            id=TaskId("task-001"),
            title=TaskTitle("Tarefa"),
            priority=TaskPriority.medium(),
            created_at=datetime.now(UTC),
        )
        task.cancel()

        # Act & Assert
        with pytest.raises(BusinessRuleViolationException):
            task.complete(datetime.now(UTC))


class TestTaskStart:
    """Testes para iniciar Task."""

    @pytest.mark.unit
    def test_start_pending_task(self) -> None:
        # Arrange
        task = Task.create(
            id=TaskId("task-001"),
            title=TaskTitle("Tarefa"),
            priority=TaskPriority.medium(),
            created_at=datetime.now(UTC),
        )

        # Act
        task.start()

        # Assert
        assert task.status.value == "in_progress"
        assert task.is_open

    @pytest.mark.unit
    def test_cannot_start_completed_task(self) -> None:
        # Arrange
        task = Task.create(
            id=TaskId("task-001"),
            title=TaskTitle("Tarefa"),
            priority=TaskPriority.medium(),
            created_at=datetime.now(UTC),
        )
        task.complete(datetime.now(UTC))

        # Act & Assert
        with pytest.raises(BusinessRuleViolationException):
            task.start()


class TestTaskEquality:
    """Testes para igualdade de entidades."""

    @pytest.mark.unit
    def test_tasks_with_same_id_are_equal(self) -> None:
        # Arrange
        task1 = Task.create(
            id=TaskId("same-id"),
            title=TaskTitle("Tarefa 1"),
            priority=TaskPriority.low(),
            created_at=datetime.now(UTC),
        )
        task2 = Task.create(
            id=TaskId("same-id"),
            title=TaskTitle("Tarefa 2"),  # título diferente
            priority=TaskPriority.high(),  # prioridade diferente
            created_at=datetime.now(UTC),
        )

        # Act & Assert
        assert task1 == task2  # Iguais pelo ID

    @pytest.mark.unit
    def test_tasks_with_different_ids_are_not_equal(self) -> None:
        # Arrange
        task1 = Task.create(
            id=TaskId("id-1"),
            title=TaskTitle("Tarefa"),
            priority=TaskPriority.medium(),
            created_at=datetime.now(UTC),
        )
        task2 = Task.create(
            id=TaskId("id-2"),
            title=TaskTitle("Tarefa"),  # mesmo título
            priority=TaskPriority.medium(),  # mesma prioridade
            created_at=datetime.now(UTC),
        )

        # Act & Assert
        assert task1 != task2
