"""Seedwork: blocos de construção táticos reutilizados por todos os bounded contexts.

Seedwork não é Shared Kernel. Aqui ficam apenas abstrações técnicas do DDD
(Entity, AggregateRoot, ValueObject...), sem nenhum conceito de negócio.
"""

from app.domain.seedwork.aggregate_root import AggregateRoot
from app.domain.seedwork.domain_event import DomainEvent
from app.domain.seedwork.entity import Entity
from app.domain.seedwork.exceptions import BusinessRuleViolation, DomainError, InvariantViolation
from app.domain.seedwork.specification import Specification
from app.domain.seedwork.value_object import ValueObject

__all__ = [
    "AggregateRoot",
    "BusinessRuleViolation",
    "DomainError",
    "DomainEvent",
    "Entity",
    "InvariantViolation",
    "Specification",
    "ValueObject",
]
