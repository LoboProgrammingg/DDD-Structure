"""
Validadores de domínio.

Este módulo contém validadores reutilizáveis para regras de domínio.
Use estes validadores dentro de entidades e value objects.
"""

import re
from typing import Any, TypeVar


from app.domain.common.exceptions import ValidationException


T = TypeVar("T")


class Validator:
    """
    Classe com métodos estáticos para validações comuns.

    Todos os métodos levantam ValidationException se a validação falhar.
    """

    @staticmethod
    def not_empty(value: str, field_name: str) -> str:
        """
        Valida que uma string não é vazia.

        Args:
            value: Valor a ser validado
            field_name: Nome do campo (para mensagem de erro)

        Returns:
            O valor validado (stripped)

        Raises:
            ValidationException: Se o valor for vazio
        """
        stripped = value.strip()
        if not stripped:
            raise ValidationException(
                f"{field_name} não pode ser vazio.",
                field=field_name,
            )
        return stripped

    @staticmethod
    def max_length(value: str, max_len: int, field_name: str) -> str:
        """
        Valida que uma string não excede o tamanho máximo.

        Args:
            value: Valor a ser validado
            max_len: Tamanho máximo permitido
            field_name: Nome do campo

        Returns:
            O valor validado

        Raises:
            ValidationException: Se exceder o tamanho máximo
        """
        if len(value) > max_len:
            raise ValidationException(
                f"{field_name} não pode ter mais de {max_len} caracteres.",
                field=field_name,
            )
        return value

    @staticmethod
    def min_length(value: str, min_len: int, field_name: str) -> str:
        """
        Valida que uma string tem tamanho mínimo.

        Args:
            value: Valor a ser validado
            min_len: Tamanho mínimo exigido
            field_name: Nome do campo

        Returns:
            O valor validado

        Raises:
            ValidationException: Se for menor que o mínimo
        """
        if len(value) < min_len:
            raise ValidationException(
                f"{field_name} deve ter pelo menos {min_len} caracteres.",
                field=field_name,
            )
        return value

    @staticmethod
    def in_range(value: int | float, min_val: int | float, max_val: int | float, field_name: str) -> int | float:
        """
        Valida que um número está dentro de um intervalo.

        Args:
            value: Valor a ser validado
            min_val: Valor mínimo
            max_val: Valor máximo
            field_name: Nome do campo

        Returns:
            O valor validado

        Raises:
            ValidationException: Se estiver fora do intervalo
        """
        if not min_val <= value <= max_val:
            raise ValidationException(
                f"{field_name} deve estar entre {min_val} e {max_val}.",
                field=field_name,
            )
        return value

    @staticmethod
    def positive(value: int | float, field_name: str) -> int | float:
        """Valida que um número é positivo (> 0)."""
        if value <= 0:
            raise ValidationException(
                f"{field_name} deve ser maior que zero.",
                field=field_name,
            )
        return value

    @staticmethod
    def not_none(value: T | None, field_name: str) -> T:
        """Valida que um valor não é None."""
        if value is None:
            raise ValidationException(
                f"{field_name} é obrigatório.",
                field=field_name,
            )
        return value

    @staticmethod
    def matches_pattern(value: str, pattern: str, field_name: str, message: str | None = None) -> str:
        """
        Valida que uma string corresponde a um padrão regex.

        Args:
            value: Valor a ser validado
            pattern: Padrão regex
            field_name: Nome do campo
            message: Mensagem de erro customizada

        Returns:
            O valor validado

        Raises:
            ValidationException: Se não corresponder ao padrão
        """
        if not re.match(pattern, value):
            error_message = message or f"{field_name} tem formato inválido."
            raise ValidationException(error_message, field=field_name)
        return value

    @staticmethod
    def is_valid_email(value: str, field_name: str = "Email") -> str:
        """Valida formato básico de email."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return Validator.matches_pattern(
            value, pattern, field_name, f"{field_name} tem formato inválido."
        )
