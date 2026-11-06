from datetime import UTC, date, datetime

from app.domain.task_management.specifications import (
    AssignedTo,
    InProgressTask,
    OpenTask,
    OverdueTask,
)
from app.domain.task_management.value_objects import AssigneeId
from tests.builders import a_started_task, a_task

NOW = datetime(2026, 1, 20, tzinfo=UTC)


def test_open_task() -> None:
    cancelled = a_task()
    cancelled.cancel()

    assert OpenTask().is_satisfied_by(a_task())
    assert not OpenTask().is_satisfied_by(cancelled)


def test_in_progress_task() -> None:
    assert InProgressTask().is_satisfied_by(a_started_task())
    assert not InProgressTask().is_satisfied_by(a_task())


def test_assigned_to() -> None:
    spec = AssignedTo(AssigneeId("ana.souza"))

    assert spec.is_satisfied_by(a_task(assignee="ana.souza"))
    assert not spec.is_satisfied_by(a_task(assignee="bruno"))
    assert not spec.is_satisfied_by(a_task())


def test_overdue_task() -> None:
    assert OverdueTask(NOW).is_satisfied_by(a_task(due_date=date(2026, 1, 16)))
    assert not OverdueTask(NOW).is_satisfied_by(a_task(due_date=date(2026, 1, 25)))


def test_specifications_compose_into_new_business_rules() -> None:
    overdue_for_ana = OverdueTask(NOW) & AssignedTo(AssigneeId("ana.souza"))

    assert overdue_for_ana.is_satisfied_by(a_task(assignee="ana.souza", due_date=date(2026, 1, 16)))
    assert not overdue_for_ana.is_satisfied_by(a_task(assignee="bruno", due_date=date(2026, 1, 16)))
