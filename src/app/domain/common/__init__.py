"""
Building blocks comuns do domínio.

Este módulo contém as classes base e utilitários que são usados
por todos os bounded contexts do domínio.
"""

from app.domain.common.entity import Entity
from app.domain.common.events import DomainEvent, EventMixin
from app.domain.common.exceptions import DomainException, ValidationException
from app.domain.common.result import Failure, Result, Success
from app.domain.common.validators import Validator
from app.domain.common.value_object import ValueObject


__all__ = [
    "Entity",
    "ValueObject",
    "DomainEvent",
    "EventMixin",
    "DomainException",
    "ValidationException",
    "Result",
    "Success",
    "Failure",
    "Validator",
]
