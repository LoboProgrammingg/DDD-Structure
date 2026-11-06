from enum import StrEnum

from app.domain.task_management.exceptions import InvalidTaskPriority


class TaskPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

    @classmethod
    def parse(cls, raw: str) -> "TaskPriority":
        try:
            return cls(raw.strip().lower())
        except ValueError:
            allowed = ", ".join(priority.value for priority in cls)
            raise InvalidTaskPriority(
                f"Prioridade '{raw}' inválida. Valores aceitos: {allowed}."
            ) from None
