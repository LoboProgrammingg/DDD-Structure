"""
Base class para Use Cases.

Use Cases representam as operações que o sistema pode executar.
Cada use case implementa uma única operação de negócio.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar


TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")


class UseCase(ABC, Generic[TInput, TOutput]):
    """
    Classe base para todos os use cases.

    Um use case:
    - Executa uma única operação de negócio
    - Recebe um input (command/query)
    - Retorna um output (result/response)
    - Orquestra entidades e serviços de domínio
    - Não contém lógica de negócio (isso fica no domínio)

    Exemplo de uso:
        >>> class CreateUserUseCase(UseCase[CreateUserInput, UserOutput]):
        ...     def execute(self, input: CreateUserInput) -> UserOutput:
        ...         user = User.create(input.email, input.name)
        ...         self.repository.save(user)
        ...         return UserOutput.from_entity(user)
    """

    @abstractmethod
    def execute(self, input: TInput) -> TOutput:
        """
        Executa o use case.

        Args:
            input: Dados de entrada para o use case

        Returns:
            Resultado da operação
        """
