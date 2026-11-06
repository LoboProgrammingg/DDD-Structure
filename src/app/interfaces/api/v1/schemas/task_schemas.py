"""Contratos HTTP. Validam o formato da requisição; as regras ficam no domínio."""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

type Priority = Literal["low", "medium", "high", "urgent"]
type Status = Literal["pending", "in_progress", "completed", "cancelled"]


class CreateTaskRequest(BaseModel):
    title: str = Field(examples=["Escrever o glossário da Linguagem Ubíqua"])
    priority: Priority = "medium"
    description: str = ""
    due_date: date | None = None


class RenameTaskRequest(BaseModel):
    title: str


class ReprioritizeTaskRequest(BaseModel):
    priority: Priority


class AssignTaskRequest(BaseModel):
    assignee_id: str = Field(examples=["ana.souza"])


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    priority: Priority
    status: Status
    assignee_id: str | None
    due_date: date | None
    created_at: datetime
    completed_at: datetime | None
    version: int


class TaskPageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[TaskResponse]
    total: int
    limit: int
    offset: int
