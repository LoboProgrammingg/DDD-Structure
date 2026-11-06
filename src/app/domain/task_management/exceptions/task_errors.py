"""Erros tipados do contexto Task Management, nomeados na Linguagem Ubíqua."""

from typing import ClassVar

from app.domain.seedwork import BusinessRuleViolation, InvariantViolation


class InvalidTaskId(InvariantViolation):
    code: ClassVar[str] = "invalid_task_id"


class InvalidTaskTitle(InvariantViolation):
    code: ClassVar[str] = "invalid_task_title"


class InvalidTaskDescription(InvariantViolation):
    code: ClassVar[str] = "invalid_task_description"


class InvalidTaskPriority(InvariantViolation):
    code: ClassVar[str] = "invalid_task_priority"


class InvalidAssignee(InvariantViolation):
    code: ClassVar[str] = "invalid_assignee"


class DueDateBeforeCreation(BusinessRuleViolation):
    code: ClassVar[str] = "due_date_before_creation"


class TaskIsClosed(BusinessRuleViolation):
    code: ClassVar[str] = "task_is_closed"


class InvalidStatusTransition(BusinessRuleViolation):
    code: ClassVar[str] = "invalid_status_transition"


class TaskNotAssigned(BusinessRuleViolation):
    code: ClassVar[str] = "task_not_assigned"


class WorkInProgressLimitExceeded(BusinessRuleViolation):
    code: ClassVar[str] = "work_in_progress_limit_exceeded"
