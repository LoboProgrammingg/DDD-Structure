"""
Testes unitários para Use Cases.
"""

import pytest

from app.application.common.errors import NotFoundError
from app.application.sample_context.use_cases import (
    CompleteTaskUseCase,
    CreateTaskUseCase,
    ListTasksUseCase,
    RenameTaskUseCase,
)
from app.application.sample_context.use_cases.complete_task import CompleteTaskInput
from app.application.sample_context.use_cases.create_task import CreateTaskInput
from app.application.sample_context.use_cases.list_tasks import ListTasksInput, TaskFilter
from app.application.sample_context.use_cases.rename_task import RenameTaskInput
from app.infrastructure.persistence.in_memory.task_repository import InMemoryTaskRepository
from tests.conftest import FakeClock, FakeIdGenerator


@pytest.fixture
def repository() -> InMemoryTaskRepository:
    """Fixture que fornece um repositório in-memory limpo."""
    return InMemoryTaskRepository()


class TestCreateTaskUseCase:
    """Testes para CreateTaskUseCase."""

    @pytest.mark.unit
    def test_create_task_successfully(
        self,
        repository: InMemoryTaskRepository,
        fake_clock: FakeClock,
        fake_id_generator: FakeIdGenerator,
    ) -> None:
        # Arrange
        use_case = CreateTaskUseCase(
            repository=repository,
            clock=fake_clock,
            id_generator=fake_id_generator,
        )
        input_data = CreateTaskInput(
            title="Nova tarefa",
            priority="high",
            description="Descrição da tarefa",
        )

        # Act
        output = use_case.execute(input_data)

        # Assert
        assert output.id == "test-0001"
        assert output.title == "Nova tarefa"
        assert output.priority == "high"
        assert output.status == "pending"
        assert repository.count() == 1

    @pytest.mark.unit
    def test_create_task_with_default_priority(
        self,
        repository: InMemoryTaskRepository,
        fake_clock: FakeClock,
        fake_id_generator: FakeIdGenerator,
    ) -> None:
        # Arrange
        use_case = CreateTaskUseCase(
            repository=repository,
            clock=fake_clock,
            id_generator=fake_id_generator,
        )
        input_data = CreateTaskInput(title="Tarefa simples")

        # Act
        output = use_case.execute(input_data)

        # Assert
        assert output.priority == "medium"


class TestCompleteTaskUseCase:
    """Testes para CompleteTaskUseCase."""

    @pytest.mark.unit
    def test_complete_existing_task(
        self,
        repository: InMemoryTaskRepository,
        fake_clock: FakeClock,
        fake_id_generator: FakeIdGenerator,
    ) -> None:
        # Arrange - criar uma tarefa primeiro
        create_use_case = CreateTaskUseCase(
            repository=repository,
            clock=fake_clock,
            id_generator=fake_id_generator,
        )
        created = create_use_case.execute(CreateTaskInput(title="Tarefa"))

        complete_use_case = CompleteTaskUseCase(
            repository=repository,
            clock=fake_clock,
        )

        # Act
        output = complete_use_case.execute(CompleteTaskInput(task_id=created.id))

        # Assert
        assert output.status == "completed"
        assert output.completed_at is not None

    @pytest.mark.unit
    def test_complete_nonexistent_task_raises_error(
        self,
        repository: InMemoryTaskRepository,
        fake_clock: FakeClock,
    ) -> None:
        # Arrange
        use_case = CompleteTaskUseCase(
            repository=repository,
            clock=fake_clock,
        )

        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            use_case.execute(CompleteTaskInput(task_id="nonexistent"))

        assert exc_info.value.identifier == "nonexistent"


class TestRenameTaskUseCase:
    """Testes para RenameTaskUseCase."""

    @pytest.mark.unit
    def test_rename_existing_task(
        self,
        repository: InMemoryTaskRepository,
        fake_clock: FakeClock,
        fake_id_generator: FakeIdGenerator,
    ) -> None:
        # Arrange
        create_use_case = CreateTaskUseCase(
            repository=repository,
            clock=fake_clock,
            id_generator=fake_id_generator,
        )
        created = create_use_case.execute(CreateTaskInput(title="Título original"))

        rename_use_case = RenameTaskUseCase(repository=repository)

        # Act
        output = rename_use_case.execute(
            RenameTaskInput(task_id=created.id, new_title="Novo título")
        )

        # Assert
        assert output.old_title == "Título original"
        assert output.new_title == "Novo título"

    @pytest.mark.unit
    def test_rename_nonexistent_task_raises_error(
        self,
        repository: InMemoryTaskRepository,
    ) -> None:
        # Arrange
        use_case = RenameTaskUseCase(repository=repository)

        # Act & Assert
        with pytest.raises(NotFoundError):
            use_case.execute(RenameTaskInput(task_id="nonexistent", new_title="Novo"))


class TestListTasksUseCase:
    """Testes para ListTasksUseCase."""

    @pytest.mark.unit
    def test_list_all_tasks(
        self,
        repository: InMemoryTaskRepository,
        fake_clock: FakeClock,
        fake_id_generator: FakeIdGenerator,
    ) -> None:
        # Arrange - criar algumas tarefas
        create_use_case = CreateTaskUseCase(
            repository=repository,
            clock=fake_clock,
            id_generator=fake_id_generator,
        )
        create_use_case.execute(CreateTaskInput(title="Tarefa 1"))
        create_use_case.execute(CreateTaskInput(title="Tarefa 2"))
        create_use_case.execute(CreateTaskInput(title="Tarefa 3"))

        list_use_case = ListTasksUseCase(repository=repository)

        # Act
        output = list_use_case.execute(ListTasksInput(filter=TaskFilter.ALL))

        # Assert
        assert output.total == 3
        assert len(output.tasks) == 3

    @pytest.mark.unit
    def test_list_pending_tasks(
        self,
        repository: InMemoryTaskRepository,
        fake_clock: FakeClock,
        fake_id_generator: FakeIdGenerator,
    ) -> None:
        # Arrange
        create_use_case = CreateTaskUseCase(
            repository=repository,
            clock=fake_clock,
            id_generator=fake_id_generator,
        )
        created1 = create_use_case.execute(CreateTaskInput(title="Tarefa 1"))
        create_use_case.execute(CreateTaskInput(title="Tarefa 2"))

        # Completar uma tarefa
        complete_use_case = CompleteTaskUseCase(
            repository=repository,
            clock=fake_clock,
        )
        complete_use_case.execute(CompleteTaskInput(task_id=created1.id))

        list_use_case = ListTasksUseCase(repository=repository)

        # Act
        output = list_use_case.execute(ListTasksInput(filter=TaskFilter.PENDING))

        # Assert
        assert output.total == 1
        assert output.tasks[0].title == "Tarefa 2"

    @pytest.mark.unit
    def test_list_completed_tasks(
        self,
        repository: InMemoryTaskRepository,
        fake_clock: FakeClock,
        fake_id_generator: FakeIdGenerator,
    ) -> None:
        # Arrange
        create_use_case = CreateTaskUseCase(
            repository=repository,
            clock=fake_clock,
            id_generator=fake_id_generator,
        )
        created = create_use_case.execute(CreateTaskInput(title="Tarefa 1"))
        create_use_case.execute(CreateTaskInput(title="Tarefa 2"))

        complete_use_case = CompleteTaskUseCase(
            repository=repository,
            clock=fake_clock,
        )
        complete_use_case.execute(CompleteTaskInput(task_id=created.id))

        list_use_case = ListTasksUseCase(repository=repository)

        # Act
        output = list_use_case.execute(ListTasksInput(filter=TaskFilter.COMPLETED))

        # Assert
        assert output.total == 1
        assert output.tasks[0].title == "Tarefa 1"

    @pytest.mark.unit
    def test_list_empty_repository(
        self,
        repository: InMemoryTaskRepository,
    ) -> None:
        # Arrange
        use_case = ListTasksUseCase(repository=repository)

        # Act
        output = use_case.execute(ListTasksInput())

        # Assert
        assert output.total == 0
        assert output.tasks == []
