"""Endpoints orientados a comandos: cada verbo do negócio é uma ação explícita.

``POST /tasks/{id}/complete`` diz mais do que ``PATCH /tasks/{id} {"status": ...}``
e mantém a Linguagem Ubíqua também no contrato HTTP.
"""

from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from app.application.task_management.commands import (
    AssignTask,
    CancelTask,
    CompleteTask,
    CreateTask,
    RenameTask,
    ReprioritizeTask,
    StartTask,
)
from app.application.task_management.queries import GetTask, ListTasks
from app.domain.task_management.value_objects import TaskStatus
from app.interfaces.api.v1.dependencies import ContainerDep
from app.interfaces.api.v1.schemas import (
    AssignTaskRequest,
    CreateTaskRequest,
    RenameTaskRequest,
    ReprioritizeTaskRequest,
    TaskPageResponse,
    TaskResponse,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


async def _task_response(container: ContainerDep, task_id: str) -> TaskResponse:
    return TaskResponse.model_validate(await container.get_task(GetTask(task_id)))


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_task(
    body: CreateTaskRequest, container: ContainerDep, response: Response
) -> TaskResponse:
    task_id = await container.create_task(
        CreateTask(
            title=body.title,
            priority=body.priority,
            description=body.description,
            due_date=body.due_date,
        )
    )
    response.headers["Location"] = f"/api/v1/tasks/{task_id}"
    return await _task_response(container, task_id)


@router.get("")
async def list_tasks(
    container: ContainerDep,
    status_filter: Annotated[TaskStatus | None, Query(alias="status")] = None,
    assignee_id: str | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> TaskPageResponse:
    page = await container.list_tasks(
        ListTasks(status=status_filter, assignee_id=assignee_id, limit=limit, offset=offset)
    )
    return TaskPageResponse.model_validate(page)


@router.get("/{task_id}")
async def get_task(task_id: str, container: ContainerDep) -> TaskResponse:
    return await _task_response(container, task_id)


@router.post("/{task_id}/rename")
async def rename_task(
    task_id: str, body: RenameTaskRequest, container: ContainerDep
) -> TaskResponse:
    await container.rename_task(RenameTask(task_id=task_id, title=body.title))
    return await _task_response(container, task_id)


@router.post("/{task_id}/reprioritize")
async def reprioritize_task(
    task_id: str, body: ReprioritizeTaskRequest, container: ContainerDep
) -> TaskResponse:
    await container.reprioritize_task(ReprioritizeTask(task_id=task_id, priority=body.priority))
    return await _task_response(container, task_id)


@router.post("/{task_id}/assign")
async def assign_task(
    task_id: str, body: AssignTaskRequest, container: ContainerDep
) -> TaskResponse:
    await container.assign_task(AssignTask(task_id=task_id, assignee_id=body.assignee_id))
    return await _task_response(container, task_id)


@router.post("/{task_id}/start")
async def start_task(task_id: str, container: ContainerDep) -> TaskResponse:
    await container.start_task(StartTask(task_id=task_id))
    return await _task_response(container, task_id)


@router.post("/{task_id}/complete")
async def complete_task(task_id: str, container: ContainerDep) -> TaskResponse:
    await container.complete_task(CompleteTask(task_id=task_id))
    return await _task_response(container, task_id)


@router.post("/{task_id}/cancel")
async def cancel_task(task_id: str, container: ContainerDep) -> TaskResponse:
    await container.cancel_task(CancelTask(task_id=task_id))
    return await _task_response(container, task_id)
