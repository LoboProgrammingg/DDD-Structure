"""
Result Pattern para tratamento de erros.

O Result pattern permite retornar sucesso ou falha de uma operação
de forma explícita, sem usar exceções para controle de fluxo.

Este é um padrão alternativo às exceções. Escolha UM padrão e use
consistentemente em todo o projeto.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Generic, TypeVar


T = TypeVar("T")
E = TypeVar("E")
U = TypeVar("U")


class Result(ABC, Generic[T, E]):
    """
    Representa o resultado de uma operação que pode falhar.

    Use Success[T] para operações bem-sucedidas.
    Use Failure[E] para operações que falharam.

    Exemplo de uso:
        >>> def divide(a: int, b: int) -> Result[float, str]:
        ...     if b == 0:
        ...         return Failure("Divisão por zero")
        ...     return Success(a / b)
        ...
        >>> result = divide(10, 2)
        >>> if result.is_success:
        ...     print(f"Resultado: {result.value}")
        >>> else:
        ...     print(f"Erro: {result.error}")
    """

    @property
    @abstractmethod
    def is_success(self) -> bool:
        """Retorna True se a operação foi bem-sucedida."""

    @property
    @abstractmethod
    def is_failure(self) -> bool:
        """Retorna True se a operação falhou."""

    @property
    @abstractmethod
    def value(self) -> T:
        """Retorna o valor em caso de sucesso. Levanta erro se for Failure."""

    @property
    @abstractmethod
    def error(self) -> E:
        """Retorna o erro em caso de falha. Levanta erro se for Success."""

    def map(self, func: Callable[[T], U]) -> "Result[U, E]":
        """
        Aplica uma função ao valor se for Success.

        Args:
            func: Função a ser aplicada ao valor

        Returns:
            Novo Result com o valor transformado ou o erro original
        """
        if self.is_success:
            return Success(func(self.value))
        return Failure(self.error)

    def flat_map(self, func: Callable[[T], "Result[U, E]"]) -> "Result[U, E]":
        """
        Aplica uma função que retorna Result ao valor se for Success.

        Args:
            func: Função que retorna um Result

        Returns:
            Result da função aplicada ou o erro original
        """
        if self.is_success:
            return func(self.value)
        return Failure(self.error)

    def on_success(self, func: Callable[[T], None]) -> "Result[T, E]":
        """
        Executa uma função se for Success, retorna self.

        Útil para side effects como logging.
        """
        if self.is_success:
            func(self.value)
        return self

    def on_failure(self, func: Callable[[E], None]) -> "Result[T, E]":
        """
        Executa uma função se for Failure, retorna self.

        Útil para side effects como logging.
        """
        if self.is_failure:
            func(self.error)
        return self

    def unwrap_or(self, default: T) -> T:
        """Retorna o valor ou um default se for Failure."""
        if self.is_success:
            return self.value
        return default

    def unwrap_or_else(self, func: Callable[[E], T]) -> T:
        """Retorna o valor ou o resultado de uma função aplicada ao erro."""
        if self.is_success:
            return self.value
        return func(self.error)


class Success(Result[T, E]):
    """Representa o sucesso de uma operação com um valor."""

    __slots__ = ("_value",)

    def __init__(self, value: T) -> None:
        self._value = value

    @property
    def is_success(self) -> bool:
        return True

    @property
    def is_failure(self) -> bool:
        return False

    @property
    def value(self) -> T:
        return self._value

    @property
    def error(self) -> E:
        raise ValueError("Cannot get error from Success result")

    def __repr__(self) -> str:
        return f"Success({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Success):
            return NotImplemented
        return self._value == other._value


class Failure(Result[T, E]):
    """Representa a falha de uma operação com um erro."""

    __slots__ = ("_error",)

    def __init__(self, error: E) -> None:
        self._error = error

    @property
    def is_success(self) -> bool:
        return False

    @property
    def is_failure(self) -> bool:
        return True

    @property
    def value(self) -> T:
        raise ValueError(f"Cannot get value from Failure result: {self._error}")

    @property
    def error(self) -> E:
        return self._error

    def __repr__(self) -> str:
        return f"Failure({self._error!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Failure):
            return NotImplemented
        return self._error == other._error
