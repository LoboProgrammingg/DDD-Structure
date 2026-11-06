import uuid
from datetime import UTC, date, datetime

import pytest

from app.domain.task_management.exceptions import (
    InvalidAssignee,
    InvalidTaskDescription,
    InvalidTaskId,
    InvalidTaskPriority,
    InvalidTaskTitle,
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


class TestTaskId:
    def test_parses_a_uuid_string(self) -> None:
        raw = str(uuid.uuid4())
        assert str(TaskId.from_string(raw)) == raw

    @pytest.mark.parametrize("raw", ["", "123", "not-a-uuid"])
    def test_rejects_malformed_identifiers(self, raw: str) -> None:
        with pytest.raises(InvalidTaskId):
            TaskId.from_string(raw)


class TestTaskTitle:
    def test_collapses_whitespace(self) -> None:
        assert TaskTitle("  Revisar   o   contrato ").value == "Revisar o contrato"

    @pytest.mark.parametrize("raw", ["", "   ", "x" * 121])
    def test_rejects_empty_or_too_long(self, raw: str) -> None:
        with pytest.raises(InvalidTaskTitle):
            TaskTitle(raw)

    def test_accepts_the_maximum_length(self) -> None:
        assert len(TaskTitle("x" * 120).value) == 120


class TestTaskDescription:
    def test_defaults_to_empty(self) -> None:
        assert TaskDescription().is_empty

    def test_rejects_too_long(self) -> None:
        with pytest.raises(InvalidTaskDescription):
            TaskDescription("x" * 2001)


class TestTaskPriority:
    @pytest.mark.parametrize("raw", ["high", " HIGH "])
    def test_parse_is_lenient_with_case_and_spaces(self, raw: str) -> None:
        assert TaskPriority.parse(raw) is TaskPriority.HIGH

    def test_parse_rejects_unknown_values(self) -> None:
        with pytest.raises(InvalidTaskPriority, match="low, medium, high, urgent"):
            TaskPriority.parse("critical")


class TestTaskStatus:
    @pytest.mark.parametrize(
        ("source", "target", "allowed"),
        [
            (TaskStatus.PENDING, TaskStatus.IN_PROGRESS, True),
            (TaskStatus.PENDING, TaskStatus.COMPLETED, True),
            (TaskStatus.PENDING, TaskStatus.CANCELLED, True),
            (TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED, True),
            (TaskStatus.IN_PROGRESS, TaskStatus.PENDING, False),
            (TaskStatus.COMPLETED, TaskStatus.IN_PROGRESS, False),
            (TaskStatus.CANCELLED, TaskStatus.PENDING, False),
        ],
    )
    def test_transitions(self, source: TaskStatus, target: TaskStatus, allowed: bool) -> None:
        assert source.can_transition_to(target) is allowed

    def test_only_pending_and_in_progress_are_open(self) -> None:
        assert {status for status in TaskStatus if status.is_open} == {
            TaskStatus.PENDING,
            TaskStatus.IN_PROGRESS,
        }


class TestDueDate:
    def test_is_before_compares_calendar_days(self) -> None:
        due = DueDate(date(2026, 1, 15))

        assert due.is_before(datetime(2026, 1, 16, 0, 0, tzinfo=UTC))
        assert not due.is_before(datetime(2026, 1, 15, 23, 59, tzinfo=UTC))


class TestAssigneeId:
    @pytest.mark.parametrize("raw", ["", "  ", "x" * 65])
    def test_rejects_invalid_identifiers(self, raw: str) -> None:
        with pytest.raises(InvalidAssignee):
            AssigneeId(raw)

    def test_strips_spaces(self) -> None:
        assert AssigneeId(" ana.souza ") == AssigneeId("ana.souza")
