"""Erros da camada de aplicação (falhas de orquestração, não de regra de negócio)."""

from typing import ClassVar


class ApplicationError(Exception):
    code: ClassVar[str] = "application_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(ApplicationError):
    code: ClassVar[str] = "not_found"

    def __init__(self, resource: str, identifier: str) -> None:
        super().__init__(f"{resource} '{identifier}' não encontrado(a).")
        self.resource = resource
        self.identifier = identifier


class ConcurrencyConflictError(ApplicationError):
    code: ClassVar[str] = "concurrency_conflict"

    def __init__(self) -> None:
        super().__init__("O recurso foi alterado por outra operação. Recarregue e tente novamente.")
