from abc import ABC
from collections.abc import Callable

from app.application.shared import UnitOfWork
from app.domain.task_management.repositories import TaskRepository


class TaskManagementUnitOfWork(UnitOfWork, ABC):
    tasks: TaskRepository


type TaskManagementUnitOfWorkFactory = Callable[[], TaskManagementUnitOfWork]
