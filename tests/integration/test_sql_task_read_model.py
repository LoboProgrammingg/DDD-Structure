from collections.abc import Callable
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.task_management.value_objects import TaskStatus
from app.infrastructure.read_models import SqlTaskReadModel
from app.infrastructure.unit_of_work import SqlAlchemyTaskManagementUnitOfWork
from tests.builders import CREATED_AT, a_task

type UowFactory = Callable[[], SqlAlchemyTaskManagementUnitOfWork]


async def test_get_returns_a_dto(
    task_uow: UowFactory, session_factory: async_sessionmaker[AsyncSession]
) -> None:
    task = a_task(title="Projeção")
    async with task_uow() as uow:
        await uow.tasks.add(task)
        await uow.commit()

    dto = await SqlTaskReadModel(session_factory).get(str(task.id))

    assert dto is not None
    assert (dto.id, dto.title, dto.status, dto.version) == (str(task.id), "Projeção", "pending", 1)


async def test_list_filters_paginates_and_orders_newest_first(
    task_uow: UowFactory, session_factory: async_sessionmaker[AsyncSession]
) -> None:
    async with task_uow() as uow:
        for index in range(3):
            await uow.tasks.add(
                a_task(
                    title=f"Tarefa {index}",
                    assignee="ana",
                    created_at=CREATED_AT + timedelta(minutes=index),
                )
            )
        cancelled = a_task(assignee="ana")
        cancelled.cancel()
        await uow.tasks.add(cancelled)
        await uow.tasks.add(a_task(assignee="bruno"))
        await uow.commit()

    page = await SqlTaskReadModel(session_factory).list(
        status=TaskStatus.PENDING, assignee_id="ana", limit=2, offset=0
    )

    assert page.total == 3
    assert [item.title for item in page.items] == ["Tarefa 2", "Tarefa 1"]
