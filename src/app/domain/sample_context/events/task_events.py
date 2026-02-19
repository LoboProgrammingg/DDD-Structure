"""
Domain Events do contexto de tarefas.

Eventos que representam mudanças significativas no ciclo de vida de uma tarefa.
"""

from dataclasses import dataclass

from app.domain.common.events import DomainEvent


@dataclass(frozen=True)
class TaskCreated(DomainEvent):
    """Evento disparado quando uma nova tarefa é criada."""

    task_id: str
    title: str
    priority: str


@dataclass(frozen=True)
class TaskCompleted(DomainEvent):
    """Evento disparado quando uma tarefa é marcada como concluída."""

    task_id: str
    title: str


@dataclass(frozen=True)
class TaskRenamed(DomainEvent):
    """Evento disparado quando o título de uma tarefa é alterado."""

    task_id: str
    old_title: str
    new_title: str


@dataclass(frozen=True)
class TaskPriorityChanged(DomainEvent):
    """Evento disparado quando a prioridade de uma tarefa é alterada."""

    task_id: str
    old_priority: str
    new_priority: str


@dataclass(frozen=True)
class TaskCancelled(DomainEvent):
    """Evento disparado quando uma tarefa é cancelada."""

    task_id: str
    title: str
