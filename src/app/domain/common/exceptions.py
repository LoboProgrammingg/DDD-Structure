"""
Exceções de domínio.

Este módulo define as exceções base usadas em toda a camada de domínio.
Essas exceções representam violações de regras de negócio ou invariantes.
"""


class DomainException(Exception):
    """
    Exceção base para todas as exceções de domínio.

    Use esta exceção ou suas subclasses para representar
    violações de regras de negócio.
    """

    def __init__(self, message: str, code: str | None = None) -> None:
        """
        Args:
            message: Mensagem descritiva do erro
            code: Código único para identificar o tipo de erro (opcional)
        """
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, code={self.code!r})"


class ValidationException(DomainException):
    """
    Exceção para erros de validação de domínio.

    Use para indicar que um valor ou estado viola as regras de validação.
    """

    def __init__(
        self,
        message: str,
        field: str | None = None,
        code: str = "VALIDATION_ERROR",
    ) -> None:
        """
        Args:
            message: Mensagem descritiva do erro
            field: Nome do campo que falhou na validação (opcional)
            code: Código do erro
        """
        super().__init__(message, code)
        self.field = field

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, field={self.field!r}, code={self.code!r})"
        )


class EntityNotFoundException(DomainException):
    """Exceção quando uma entidade não é encontrada."""

    def __init__(self, entity_type: str, entity_id: str) -> None:
        super().__init__(
            f"{entity_type} com ID '{entity_id}' não encontrado(a).",
            code="ENTITY_NOT_FOUND",
        )
        self.entity_type = entity_type
        self.entity_id = entity_id


class BusinessRuleViolationException(DomainException):
    """Exceção para violações de regras de negócio."""

    def __init__(self, rule: str, message: str) -> None:
        super().__init__(message, code="BUSINESS_RULE_VIOLATION")
        self.rule = rule
