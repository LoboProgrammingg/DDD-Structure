"""
Componentes comuns da camada de aplicação.

Contém classes base para use cases, DTOs e tratamento de erros.
"""

from app.application.common.dto import DTO
from app.application.common.errors import ApplicationError, NotFoundError, ValidationError
from app.application.common.use_case import UseCase


__all__ = [
    "UseCase",
    "DTO",
    "ApplicationError",
    "NotFoundError",
    "ValidationError",
]
