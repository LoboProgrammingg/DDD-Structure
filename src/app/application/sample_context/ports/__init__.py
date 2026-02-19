"""Ports (interfaces) do sample context."""

from app.application.sample_context.ports.clock import Clock
from app.application.sample_context.ports.id_generator import IdGenerator
from app.application.sample_context.ports.repositories import TaskRepositoryPort


__all__ = [
    "TaskRepositoryPort",
    "Clock",
    "IdGenerator",
]
