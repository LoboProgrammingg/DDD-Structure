"""
Erros da camada de aplicação.

Estes erros representam falhas no nível de aplicação,
como recursos não encontrados ou validações de input.
"""


class ApplicationError(Exception):
    """Erro base para erros de aplicação."""

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


class NotFoundError(ApplicationError):
    """Erro quando um recurso não é encontrado."""

    def __init__(self, resource: str, identifier: str) -> None:
        super().__init__(
            f"{resource} com identificador '{identifier}' não encontrado.",
            code="NOT_FOUND",
        )
        self.resource = resource
        self.identifier = identifier


class ValidationError(ApplicationError):
    """Erro de validação de input."""

    def __init__(self, message: str, field: str | None = None) -> None:
        super().__init__(message, code="VALIDATION_ERROR")
        self.field = field


class ConflictError(ApplicationError):
    """Erro quando há conflito (ex: recurso já existe)."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="CONFLICT")


class UnauthorizedError(ApplicationError):
    """Erro de autorização."""

    def __init__(self, message: str = "Não autorizado.") -> None:
        super().__init__(message, code="UNAUTHORIZED")
