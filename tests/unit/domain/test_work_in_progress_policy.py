import pytest

from app.domain.task_management.exceptions import TaskNotAssigned, WorkInProgressLimitExceeded
from app.domain.task_management.services import WorkInProgressPolicy
from app.domain.task_management.value_objects import TaskStatus
from tests.builders import a_started_task, a_task


def test_starts_task_when_below_the_limit() -> None:
    task = a_task(assignee="ana.souza")

    WorkInProgressPolicy(limit=2).start(task, [a_started_task("ana.souza"), task])

    assert task.status is TaskStatus.IN_PROGRESS


def test_rejects_start_when_limit_is_reached() -> None:
    task = a_task(assignee="ana.souza")
    ongoing = [a_started_task("ana.souza"), a_started_task("ana.souza")]

    with pytest.raises(WorkInProgressLimitExceeded, match="limite: 2"):
        WorkInProgressPolicy(limit=2).start(task, [*ongoing, task])

    assert task.status is TaskStatus.PENDING


def test_pending_and_closed_tasks_do_not_count() -> None:
    task = a_task(assignee="ana.souza")
    done = a_started_task("ana.souza")
    done.cancel()

    WorkInProgressPolicy(limit=1).start(task, [a_task(assignee="ana.souza"), done])

    assert task.status is TaskStatus.IN_PROGRESS


def test_unassigned_task_cannot_start() -> None:
    with pytest.raises(TaskNotAssigned):
        WorkInProgressPolicy().start(a_task(), [])


def test_limit_must_be_positive() -> None:
    with pytest.raises(ValueError, match="maior que zero"):
        WorkInProgressPolicy(limit=0)
