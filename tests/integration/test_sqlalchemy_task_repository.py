from collections.abc import Callable
from datetime import date

from app.domain.task_management.value_objects import AssigneeId, TaskStatus, TaskTitle
from app.infrastructure.unit_of_work import SqlAlchemyTaskManagementUnitOfWork
from tests.builders import a_task

type UowFactory = Callable[[], SqlAlchemyTaskManagementUnitOfWork]


async def test_round_trip_preserves_the_whole_aggregate(task_uow: UowFactory) -> None:
    original = a_task(title="Persistir agregado", due_date=date(2026, 3, 1), assignee="ana")
    async with task_uow() as uow:
        await uow.tasks.add(original)
        await uow.commit()

    async with task_uow() as uow:
        loaded = await uow.tasks.get(original.id)

    assert loaded is not None
    assert loaded.title == original.title
    assert loaded.priority is original.priority
    assert loaded.status is TaskStatus.PENDING
    assert loaded.due_date == original.due_date
    assert loaded.assignee_id == AssigneeId("ana")
    assert loaded.created_at == original.created_at
    assert loaded.version == 1


async def test_changes_are_saved_without_an_explicit_save_call(task_uow: UowFactory) -> None:
    task = a_task()
    async with task_uow() as uow:
        await uow.tasks.add(task)
        await uow.commit()

    async with task_uow() as uow:
        loaded = await uow.tasks.get(task.id)
        assert loaded is not None
        loaded.rename(TaskTitle("Renomeada"))
        await uow.commit()

    async with task_uow() as uow:
        reloaded = await uow.tasks.get(task.id)
        assert reloaded is not None
        assert reloaded.title == TaskTitle("Renomeada")
        assert reloaded.version == 2


async def test_unchanged_aggregate_keeps_its_version(task_uow: UowFactory) -> None:
    task = a_task()
    async with task_uow() as uow:
        await uow.tasks.add(task)
        await uow.commit()

    async with task_uow() as uow:
        await uow.tasks.get(task.id)
        await uow.commit()

    async with task_uow() as uow:
        reloaded = await uow.tasks.get(task.id)
        assert reloaded is not None
        assert reloaded.version == 1


async def test_identity_map_returns_the_same_instance(task_uow: UowFactory) -> None:
    task = a_task(assignee="ana")
    async with task_uow() as uow:
        await uow.tasks.add(task)
        await uow.commit()

    async with task_uow() as uow:
        by_id = await uow.tasks.get(task.id)
        [by_assignee] = await uow.tasks.list_by_assignee(AssigneeId("ana"))

    assert by_id is by_assignee


async def test_list_by_assignee_filters(task_uow: UowFactory) -> None:
    async with task_uow() as uow:
        await uow.tasks.add(a_task(assignee="ana"))
        await uow.tasks.add(a_task(assignee="bruno"))
        await uow.tasks.add(a_task())
        await uow.commit()

    async with task_uow() as uow:
        found = await uow.tasks.list_by_assignee(AssigneeId("ana"))

    assert [task.assignee_id for task in found] == [AssigneeId("ana")]
