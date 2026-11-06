from dataclasses import dataclass
from datetime import datetime

from app.domain.seedwork import Specification
from app.domain.task_management.aggregates import Task
from app.domain.task_management.value_objects import AssigneeId, TaskStatus


class OpenTask(Specification[Task]):
    def is_satisfied_by(self, candidate: Task) -> bool:
        return candidate.status.is_open


class InProgressTask(Specification[Task]):
    def is_satisfied_by(self, candidate: Task) -> bool:
        return candidate.status is TaskStatus.IN_PROGRESS


@dataclass(frozen=True)
class AssignedTo(Specification[Task]):
    assignee_id: AssigneeId

    def is_satisfied_by(self, candidate: Task) -> bool:
        return candidate.assignee_id == self.assignee_id


@dataclass(frozen=True)
class OverdueTask(Specification[Task]):
    at: datetime

    def is_satisfied_by(self, candidate: Task) -> bool:
        return candidate.is_overdue(self.at)
