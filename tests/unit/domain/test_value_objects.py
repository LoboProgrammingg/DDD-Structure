"""
Testes unitários para Value Objects do sample context.
"""

import pytest

from app.domain.common.exceptions import ValidationException
from app.domain.sample_context.value_objects import (
    TaskDescription,
    TaskId,
    TaskPriority,
    TaskStatus,
    TaskTitle,
)
from app.domain.sample_context.value_objects.task_priority import PriorityLevel
from app.domain.sample_context.value_objects.task_status import StatusValue


class TestTaskId:
    """Testes para TaskId."""

    @pytest.mark.unit
    def test_create_valid_task_id(self) -> None:
        # Arrange & Act
        task_id = TaskId("abc-123")

        # Assert
        assert task_id.value == "abc-123"
        assert str(task_id) == "abc-123"

    @pytest.mark.unit
    def test_empty_task_id_raises_validation_error(self) -> None:
        # Arrange & Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            TaskId("")

        assert "não pode ser vazio" in exc_info.value.message

    @pytest.mark.unit
    def test_whitespace_task_id_raises_validation_error(self) -> None:
        # Arrange & Act & Assert
        with pytest.raises(ValidationException):
            TaskId("   ")

    @pytest.mark.unit
    def test_task_ids_with_same_value_are_equal(self) -> None:
        # Arrange
        id1 = TaskId("same-id")
        id2 = TaskId("same-id")

        # Act & Assert
        assert id1 == id2
        assert hash(id1) == hash(id2)

    @pytest.mark.unit
    def test_task_ids_with_different_values_are_not_equal(self) -> None:
        # Arrange
        id1 = TaskId("id-1")
        id2 = TaskId("id-2")

        # Act & Assert
        assert id1 != id2


class TestTaskTitle:
    """Testes para TaskTitle."""

    @pytest.mark.unit
    def test_create_valid_title(self) -> None:
        # Arrange & Act
        title = TaskTitle("Minha tarefa")

        # Assert
        assert title.value == "Minha tarefa"

    @pytest.mark.unit
    def test_title_trims_whitespace(self) -> None:
        # Arrange & Act
        title = TaskTitle("  Título com espaços  ")

        # Assert
        assert title.value == "Título com espaços"

    @pytest.mark.unit
    def test_empty_title_raises_validation_error(self) -> None:
        # Arrange & Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            TaskTitle("")

        assert "Título" in exc_info.value.message

    @pytest.mark.unit
    def test_title_exceeding_max_length_raises_error(self) -> None:
        # Arrange
        long_title = "a" * 201

        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            TaskTitle(long_title)

        assert "200" in exc_info.value.message


class TestTaskDescription:
    """Testes para TaskDescription."""

    @pytest.mark.unit
    def test_create_valid_description(self) -> None:
        # Arrange & Act
        desc = TaskDescription("Uma descrição detalhada")

        # Assert
        assert desc.value == "Uma descrição detalhada"
        assert not desc.is_empty

    @pytest.mark.unit
    def test_empty_description_is_allowed(self) -> None:
        # Arrange & Act
        desc = TaskDescription("")

        # Assert
        assert desc.value == ""
        assert desc.is_empty

    @pytest.mark.unit
    def test_empty_factory_method(self) -> None:
        # Arrange & Act
        desc = TaskDescription.empty()

        # Assert
        assert desc.is_empty

    @pytest.mark.unit
    def test_description_exceeding_max_length_raises_error(self) -> None:
        # Arrange
        long_desc = "a" * 2001

        # Act & Assert
        with pytest.raises(ValidationException):
            TaskDescription(long_desc)


class TestTaskPriority:
    """Testes para TaskPriority."""

    @pytest.mark.unit
    def test_create_priority_from_enum(self) -> None:
        # Arrange & Act
        priority = TaskPriority(PriorityLevel.HIGH)

        # Assert
        assert priority.level == PriorityLevel.HIGH
        assert priority.value == "high"

    @pytest.mark.unit
    def test_create_priority_from_string(self) -> None:
        # Arrange & Act
        priority = TaskPriority("medium")

        # Assert
        assert priority.level == PriorityLevel.MEDIUM

    @pytest.mark.unit
    def test_invalid_priority_raises_error(self) -> None:
        # Arrange & Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            TaskPriority("invalid")

        assert "Prioridade inválida" in exc_info.value.message

    @pytest.mark.unit
    def test_is_high_priority_for_high_and_urgent(self) -> None:
        # Arrange & Act & Assert
        assert TaskPriority.high().is_high_priority
        assert TaskPriority.urgent().is_high_priority
        assert not TaskPriority.medium().is_high_priority
        assert not TaskPriority.low().is_high_priority

    @pytest.mark.unit
    def test_factory_methods(self) -> None:
        # Arrange & Act & Assert
        assert TaskPriority.low().level == PriorityLevel.LOW
        assert TaskPriority.medium().level == PriorityLevel.MEDIUM
        assert TaskPriority.high().level == PriorityLevel.HIGH
        assert TaskPriority.urgent().level == PriorityLevel.URGENT


class TestTaskStatus:
    """Testes para TaskStatus."""

    @pytest.mark.unit
    def test_create_status_from_enum(self) -> None:
        # Arrange & Act
        status = TaskStatus(StatusValue.PENDING)

        # Assert
        assert status.status == StatusValue.PENDING
        assert status.value == "pending"

    @pytest.mark.unit
    def test_create_status_from_string(self) -> None:
        # Arrange & Act
        status = TaskStatus("completed")

        # Assert
        assert status.status == StatusValue.COMPLETED

    @pytest.mark.unit
    def test_invalid_status_raises_error(self) -> None:
        # Arrange & Act & Assert
        with pytest.raises(ValidationException):
            TaskStatus("invalid")

    @pytest.mark.unit
    def test_is_open_for_pending_and_in_progress(self) -> None:
        # Arrange & Act & Assert
        assert TaskStatus.pending().is_open
        assert TaskStatus.in_progress().is_open
        assert not TaskStatus.completed().is_open
        assert not TaskStatus.cancelled().is_open

    @pytest.mark.unit
    def test_is_completed(self) -> None:
        # Arrange & Act & Assert
        assert TaskStatus.completed().is_completed
        assert not TaskStatus.pending().is_completed
