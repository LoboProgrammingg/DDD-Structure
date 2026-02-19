"""
Composition Root - Container de Dependências.

Este é o ÚNICO lugar onde dependências são instanciadas e conectadas.
Todas as outras partes do código recebem dependências via injeção.

Benefícios:
- Centralização: todas as dependências em um lugar
- Testabilidade: fácil substituir por mocks/fakes
- Flexibilidade: troque implementações sem modificar use cases
- Documentação: mostra claramente as dependências do sistema

Uso:
    container = create_container()
    use_case = container.create_task_use_case
    result = use_case.execute(input)
"""

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from app.application.sample_context.ports import Clock, IdGenerator, TaskRepositoryPort
from app.application.sample_context.use_cases import (
    CompleteTaskUseCase,
    CreateTaskUseCase,
    ListTasksUseCase,
    RenameTaskUseCase,
)
from app.infrastructure.config import Settings, get_settings
from app.infrastructure.logging import get_logger, setup_logging
from app.infrastructure.messaging import EventDispatcher
from app.infrastructure.persistence.in_memory.task_repository import InMemoryTaskRepository
from app.infrastructure.providers import SystemClock, UUIDGenerator


if TYPE_CHECKING:
    pass

logger = get_logger(__name__)


@dataclass
class Container:
    """
    Container de dependências da aplicação.

    Agrupa todas as dependências e fornece acesso lazy a elas.
    Use cached_property para garantir que cada dependência seja criada apenas uma vez.

    Padrão: Cada bounded context pode ter seu próprio sub-container
    se o projeto crescer muito.
    """

    settings: Settings

    def __post_init__(self) -> None:
        """Configura logging após inicialização."""
        setup_logging(
            level=self.settings.log_level.value,
            format_type=self.settings.log_format,
            app_name=self.settings.app_name,
        )
        logger.info(
            "Container inicializado",
            extra={
                "environment": self.settings.environment.value,
                "debug": self.settings.debug,
            },
        )

    # ==========================================================================
    # Providers (Infrastructure Services)
    # ==========================================================================

    @cached_property
    def clock(self) -> Clock:
        """Provedor de data/hora."""
        return SystemClock()

    @cached_property
    def id_generator(self) -> IdGenerator:
        """Gerador de IDs únicos."""
        return UUIDGenerator()

    @cached_property
    def event_dispatcher(self) -> EventDispatcher:
        """Dispatcher de eventos de domínio."""
        dispatcher = EventDispatcher()

        # Registra handler global para logging de eventos
        dispatcher.register_global(self._log_domain_event)

        return dispatcher

    # ==========================================================================
    # Repositories
    # ==========================================================================

    @cached_property
    def task_repository(self) -> TaskRepositoryPort:
        """
        Repositório de tarefas.

        Por padrão usa implementação in-memory.
        Em produção, substitua por implementação real (PostgreSQL, etc.)
        """
        return InMemoryTaskRepository()

    # ==========================================================================
    # Use Cases - Sample Context
    # ==========================================================================

    @cached_property
    def create_task_use_case(self) -> CreateTaskUseCase:
        """Use case para criar tarefas."""
        return CreateTaskUseCase(
            repository=self.task_repository,
            clock=self.clock,
            id_generator=self.id_generator,
        )

    @cached_property
    def complete_task_use_case(self) -> CompleteTaskUseCase:
        """Use case para completar tarefas."""
        return CompleteTaskUseCase(
            repository=self.task_repository,
            clock=self.clock,
        )

    @cached_property
    def rename_task_use_case(self) -> RenameTaskUseCase:
        """Use case para renomear tarefas."""
        return RenameTaskUseCase(
            repository=self.task_repository,
        )

    @cached_property
    def list_tasks_use_case(self) -> ListTasksUseCase:
        """Use case para listar tarefas."""
        return ListTasksUseCase(
            repository=self.task_repository,
        )

    # ==========================================================================
    # Event Handlers
    # ==========================================================================

    @staticmethod
    def _log_domain_event(event: object) -> None:
        """Handler global que loga todos os eventos de domínio."""
        event_logger = get_logger("domain.events")
        event_logger.info(
            f"Evento de domínio: {type(event).__name__}",
            extra={
                "event_type": type(event).__name__,
                "event_data": str(event),
            },
        )


def create_container(settings: Settings | None = None) -> Container:
    """
    Factory function para criar o container.

    Args:
        settings: Configurações opcionais (usa padrão se não fornecido)

    Returns:
        Container configurado e pronto para uso
    """
    if settings is None:
        settings = get_settings()

    return Container(settings=settings)


# Singleton global para uso em toda a aplicação
_container: Container | None = None


def get_container() -> Container:
    """
    Obtém o container singleton.

    Cria o container na primeira chamada e retorna a mesma instância
    em chamadas subsequentes.
    """
    global _container
    if _container is None:
        _container = create_container()
    return _container


def reset_container() -> None:
    """
    Reseta o container singleton.

    Útil para testes onde precisamos de um container limpo.
    """
    global _container
    _container = None
