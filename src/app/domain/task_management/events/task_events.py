"""Eventos publicados pelo agregado Task.

Formam a Published Language do contexto: outros contextos dependem deles,
não do modelo interno. Por isso carregam somente tipos primitivos.
"""

from dataclasses import dataclass

from app.domain.seedwork import DomainEvent


@dataclass(frozen=True, kw_only=True)
class TaskCreated(DomainEvent):
    task_id: str
    title: str
    priority: str


@dataclass(frozen=True, kw_only=True)
class TaskRenamed(DomainEvent):
    task_id: str
    previous_title: str
    new_title: str


@dataclass(frozen=True, kw_only=True)
class TaskPriorityChanged(DomainEvent):
    task_id: str
    previous_priority: str
    new_priority: str


@dataclass(frozen=True, kw_only=True)
class TaskAssigned(DomainEvent):
    task_id: str
    title: str
    assignee_id: str


@dataclass(frozen=True, kw_only=True)
class TaskStarted(DomainEvent):
    task_id: str
    assignee_id: str


@dataclass(frozen=True, kw_only=True)
class TaskCompleted(DomainEvent):
    task_id: str
    title: str


@dataclass(frozen=True, kw_only=True)
class TaskCancelled(DomainEvent):
    task_id: str
    title: str
