"""
Testes unitários para o Composition Root (Container).
"""

import pytest

from app.application.sample_context.ports import Clock, IdGenerator, TaskRepositoryPort
from app.application.sample_context.use_cases import (
    CompleteTaskUseCase,
    CreateTaskUseCase,
    ListTasksUseCase,
    RenameTaskUseCase,
)
from app.bootstrap.container import Container, create_container, get_container, reset_container
from app.infrastructure.config import Settings
from app.infrastructure.config.settings import Environment, LogLevel
from app.infrastructure.messaging import EventDispatcher


@pytest.fixture
def test_settings() -> Settings:
    """Settings para testes."""
    return Settings(
        environment=Environment.TESTING,
        log_level=LogLevel.DEBUG,
        log_format="console",
        debug=True,
    )


@pytest.fixture
def container(test_settings: Settings) -> Container:
    """Container para testes."""
    return create_container(test_settings)


@pytest.mark.unit
class TestContainer:
    """Testes para o Container de dependências."""

    def test_should_create_container_with_settings(self, test_settings: Settings) -> None:
        # Act
        container = create_container(test_settings)

        # Assert
        assert container.settings == test_settings

    def test_should_provide_clock(self, container: Container) -> None:
        # Act
        clock = container.clock

        # Assert
        assert isinstance(clock, Clock)

    def test_should_provide_id_generator(self, container: Container) -> None:
        # Act
        id_generator = container.id_generator

        # Assert
        assert isinstance(id_generator, IdGenerator)

    def test_should_provide_event_dispatcher(self, container: Container) -> None:
        # Act
        dispatcher = container.event_dispatcher

        # Assert
        assert isinstance(dispatcher, EventDispatcher)

    def test_should_provide_task_repository(self, container: Container) -> None:
        # Act
        repository = container.task_repository

        # Assert
        assert isinstance(repository, TaskRepositoryPort)

    def test_should_provide_create_task_use_case(self, container: Container) -> None:
        # Act
        use_case = container.create_task_use_case

        # Assert
        assert isinstance(use_case, CreateTaskUseCase)

    def test_should_provide_complete_task_use_case(self, container: Container) -> None:
        # Act
        use_case = container.complete_task_use_case

        # Assert
        assert isinstance(use_case, CompleteTaskUseCase)

    def test_should_provide_rename_task_use_case(self, container: Container) -> None:
        # Act
        use_case = container.rename_task_use_case

        # Assert
        assert isinstance(use_case, RenameTaskUseCase)

    def test_should_provide_list_tasks_use_case(self, container: Container) -> None:
        # Act
        use_case = container.list_tasks_use_case

        # Assert
        assert isinstance(use_case, ListTasksUseCase)

    def test_should_return_same_instance_for_cached_properties(self, container: Container) -> None:
        # Act
        clock1 = container.clock
        clock2 = container.clock

        # Assert
        assert clock1 is clock2

    def test_should_use_same_repository_across_use_cases(self, container: Container) -> None:
        # Act
        create_uc = container.create_task_use_case
        list_uc = container.list_tasks_use_case

        # Assert - ambos devem usar o mesmo repositório
        assert create_uc._repository is list_uc._repository


@pytest.mark.unit
class TestContainerSingleton:
    """Testes para o singleton do container."""

    def setup_method(self) -> None:
        """Reset container antes de cada teste."""
        reset_container()

    def teardown_method(self) -> None:
        """Reset container depois de cada teste."""
        reset_container()

    def test_should_return_same_container_instance(self) -> None:
        # Act
        container1 = get_container()
        container2 = get_container()

        # Assert
        assert container1 is container2

    def test_should_reset_container(self) -> None:
        # Arrange
        container1 = get_container()

        # Act
        reset_container()
        container2 = get_container()

        # Assert
        assert container1 is not container2
