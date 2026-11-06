import uuid

from sqlalchemy import select

from app.domain.task_management.aggregates import Task
from app.domain.task_management.repositories import TaskRepository
from app.domain.task_management.value_objects import (
    AssigneeId,
    DueDate,
    TaskDescription,
    TaskId,
    TaskPriority,
    TaskStatus,
    TaskTitle,
)
from app.infrastructure.database.models import TaskModel
from app.infrastructure.repositories.sqlalchemy_repository import SqlAlchemyRepository


class SqlAlchemyTaskRepository(SqlAlchemyRepository[Task, TaskModel], TaskRepository):
    model = TaskModel

    def next_identity(self) -> TaskId:
        return TaskId(uuid.uuid4())

    async def add(self, task: Task) -> None:
        self._register(task)

    async def get(self, task_id: TaskId) -> Task | None:
        return await self._find(task_id.value)

    async def list_by_assignee(self, assignee_id: AssigneeId) -> list[Task]:
        rows = await self._session.scalars(
            select(TaskModel).where(TaskModel.assignee_id == assignee_id.value)
        )
        return [self._track(row) for row in rows]

    def _primary_key(self, aggregate: Task) -> uuid.UUID:
        return aggregate.id.value

    def _row_primary_key(self, row: TaskModel) -> uuid.UUID:
        return row.id

    def _to_domain(self, row: TaskModel) -> Task:
        return Task(
            TaskId(row.id),
            title=TaskTitle(row.title),
            description=TaskDescription(row.description),
            priority=TaskPriority(row.priority),
            status=TaskStatus(row.status),
            created_at=row.created_at,
            due_date=DueDate(row.due_date) if row.due_date else None,
            assignee_id=AssigneeId(row.assignee_id) if row.assignee_id else None,
            completed_at=row.completed_at,
            version=row.version,
        )

    def _apply(self, aggregate: Task, row: TaskModel) -> None:
        row.title = aggregate.title.value
        row.description = aggregate.description.value
        row.priority = aggregate.priority.value
        row.status = aggregate.status.value
        row.assignee_id = aggregate.assignee_id.value if aggregate.assignee_id else None
        row.due_date = aggregate.due_date.value if aggregate.due_date else None
        row.created_at = aggregate.created_at
        row.completed_at = aggregate.completed_at
