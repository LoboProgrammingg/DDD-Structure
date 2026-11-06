import uuid

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.task_management.dtos import TaskDTO, TaskPageDTO
from app.application.task_management.ports import TaskReadModel
from app.domain.task_management.value_objects import TaskStatus
from app.infrastructure.database.models import TaskModel


class SqlTaskReadModel(TaskReadModel):
    """Consulta direto as tabelas e devolve DTOs, sem passar pelo agregado."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def get(self, task_id: str) -> TaskDTO | None:
        async with self._session_factory() as session:
            row = await session.get(TaskModel, uuid.UUID(task_id))
            return None if row is None else _to_dto(row)

    async def list(
        self,
        *,
        status: TaskStatus | None,
        assignee_id: str | None,
        limit: int,
        offset: int,
    ) -> TaskPageDTO:
        filtered = _filtered(select(TaskModel), status, assignee_id)
        counted = _filtered(select(func.count()).select_from(TaskModel), status, assignee_id)
        page = (
            filtered.order_by(TaskModel.created_at.desc(), TaskModel.id).limit(limit).offset(offset)
        )

        async with self._session_factory() as session:
            total = await session.scalar(counted) or 0
            rows = await session.scalars(page)
            return TaskPageDTO(
                items=[_to_dto(row) for row in rows], total=total, limit=limit, offset=offset
            )


def _filtered[*Ts](
    statement: Select[*Ts], status: TaskStatus | None, assignee_id: str | None
) -> Select[*Ts]:
    if status is not None:
        statement = statement.where(TaskModel.status == status.value)
    if assignee_id is not None:
        statement = statement.where(TaskModel.assignee_id == assignee_id)
    return statement


def _to_dto(row: TaskModel) -> TaskDTO:
    return TaskDTO(
        id=str(row.id),
        title=row.title,
        description=row.description,
        priority=row.priority,
        status=row.status,
        assignee_id=row.assignee_id,
        due_date=row.due_date,
        created_at=row.created_at,
        completed_at=row.completed_at,
        version=row.version,
    )
