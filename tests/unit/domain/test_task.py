import uuid
from datetime import UTC, date, datetime

import pytest

from app.domain.task_management.aggregates import Task
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
from tests.builders import CREATED_AT, a_started_task, a_task

LATER = datetime(2026, 1, 20, 18, 0, tzinfo=UTC)


class TestCreate:
    def test_new_task_is_pending_and_records_task_created(self) -> None:
        task_id = TaskId(uuid.uuid4())

        task = Task.create(
            task_id,
            title=TaskTitle("Escrever ADR"),
            priority=TaskPriority.HIGH,
            created_at=CREATED_AT,
        )

        assert task.status is TaskStatus.PENDING
        assert task.description == TaskDescription()
        assert task.version == 0
        [event] = task.pull_events()
        assert isinstance(event, TaskCreated)
        assert (event.task_id, event.title, event.priority) == (
            str(task_id),
            "Escrever ADR",
            "high",
        )

    def test_due_date_cannot_precede_creation(self) -> None:
        with pytest.raises(DueDateBeforeCreation):
            a_task(due_date=date(2026, 1, 14))

    def test_due_date_on_creation_day_is_allowed(self) -> None:
        assert a_task(due_date=date(2026, 1, 15)).due_date == DueDate(date(2026, 1, 15))


class TestChangesWhileOpen:
    def test_rename_records_previous_and_new_title(self) -> None:
        task = a_task(title="Antigo")

        task.rename(TaskTitle("Novo"))

        [event] = task.pull_events()
        assert isinstance(event, TaskRenamed)
        assert (event.previous_title, event.new_title) == ("Antigo", "Novo")
        assert task.title == TaskTitle("Novo")

    def test_renaming_to_the_same_title_records_nothing(self) -> None:
        task = a_task(title="Igual")

        task.rename(TaskTitle("Igual"))

        assert task.pull_events() == []

    def test_reprioritize_records_change(self) -> None:
        task = a_task(priority=TaskPriority.LOW)

        task.reprioritize(TaskPriority.URGENT)

        [event] = task.pull_events()
        assert isinstance(event, TaskPriorityChanged)
        assert (event.previous_priority, event.new_priority) == ("low", "urgent")

    def test_reprioritize_to_same_priority_records_nothing(self) -> None:
        task = a_task(priority=TaskPriority.LOW)

        task.reprioritize(TaskPriority.LOW)

        assert task.pull_events() == []

    def test_assign_records_task_assigned(self) -> None:
        task = a_task(title="Modelar agregados")

        task.assign_to(AssigneeId("ana.souza"))

        [event] = task.pull_events()
        assert isinstance(event, TaskAssigned)
        assert (event.assignee_id, event.title) == ("ana.souza", "Modelar agregados")

    def test_reassigning_to_same_person_records_nothing(self) -> None:
        task = a_task(assignee="ana.souza")

        task.assign_to(AssigneeId("ana.souza"))

        assert task.pull_events() == []

    def test_describe_changes_description(self) -> None:
        task = a_task()

        task.describe(TaskDescription("Detalhes"))

        assert task.description.value == "Detalhes"


class TestLifecycle:
    def test_start_requires_an_assignee(self) -> None:
        with pytest.raises(TaskNotAssigned):
            a_task().start()

    def test_start_moves_to_in_progress(self) -> None:
        task = a_task(assignee="ana.souza")

        task.start()

        assert task.status is TaskStatus.IN_PROGRESS
        assert isinstance(task.pull_events()[0], TaskStarted)

    def test_complete_stamps_completion_time(self) -> None:
        task = a_started_task()

        task.complete(LATER)

        assert task.status is TaskStatus.COMPLETED
        assert task.completed_at == LATER
        assert isinstance(task.pull_events()[0], TaskCompleted)

    def test_pending_task_can_be_completed_directly(self) -> None:
        task = a_task()

        task.complete(LATER)

        assert task.status is TaskStatus.COMPLETED

    def test_cancel_records_task_cancelled(self) -> None:
        task = a_task()

        task.cancel()

        assert task.status is TaskStatus.CANCELLED
        assert isinstance(task.pull_events()[0], TaskCancelled)

    def test_completed_task_cannot_be_completed_again(self) -> None:
        task = a_task()
        task.complete(LATER)

        with pytest.raises(InvalidStatusTransition):
            task.complete(LATER)

    def test_cancelled_task_cannot_be_started(self) -> None:
        task = a_task(assignee="ana.souza")
        task.cancel()

        with pytest.raises(InvalidStatusTransition):
            task.start()

    @pytest.mark.parametrize(
        "change",
        [
            lambda task: task.rename(TaskTitle("Outro")),
            lambda task: task.describe(TaskDescription("Outra")),
            lambda task: task.reprioritize(TaskPriority.HIGH),
            lambda task: task.assign_to(AssigneeId("bruno")),
        ],
    )
    def test_closed_task_rejects_changes(self, change: object) -> None:
        task = a_task()
        task.cancel()

        with pytest.raises(TaskIsClosed):
            change(task)  # type: ignore[operator]


class TestOverdue:
    def test_open_task_past_due_date_is_overdue(self) -> None:
        task = a_task(due_date=date(2026, 1, 16))

        assert task.is_overdue(datetime(2026, 1, 17, tzinfo=UTC))
        assert not task.is_overdue(datetime(2026, 1, 16, 23, 0, tzinfo=UTC))

    def test_closed_or_undated_tasks_are_never_overdue(self) -> None:
        done = a_task(due_date=date(2026, 1, 16))
        done.complete(LATER)

        assert not done.is_overdue(datetime(2026, 2, 1, tzinfo=UTC))
        assert not a_task().is_overdue(datetime(2026, 2, 1, tzinfo=UTC))
