"""
Testes de integração para o workflow completo de tarefas.

Estes testes verificam a integração entre use cases e repositório.
"""

import pytest

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
from app.domain.common.exceptions import BusinessRuleViolationException
from app.infrastructure.persistence.in_memory.task_repository import InMemoryTaskRepository
from app.infrastructure.providers import SystemClock, UUIDGenerator


@pytest.fixture
def repository() -> InMemoryTaskRepository:
    """Repositório in-memory para testes de integração."""
    return InMemoryTaskRepository()


@pytest.fixture
def clock() -> SystemClock:
    """Clock real para testes de integração."""
    return SystemClock()


@pytest.fixture
def id_generator() -> UUIDGenerator:
    """Gerador de UUIDs para testes de integração."""
    return UUIDGenerator()


class TestTaskWorkflow:
    """Testes de integração do workflow de tarefas."""

    @pytest.mark.integration
    def test_complete_task_workflow(
        self,
        repository: InMemoryTaskRepository,
        clock: SystemClock,
        id_generator: UUIDGenerator,
    ) -> None:
        """
        Testa o fluxo completo:
        1. Criar tarefa
        2. Renomear tarefa
        3. Completar tarefa
        4. Verificar na listagem
        """
        # 1. Criar tarefa
        create_use_case = CreateTaskUseCase(
            repository=repository,
            clock=clock,
            id_generator=id_generator,
        )
        created = create_use_case.execute(
            CreateTaskInput(
                title="Tarefa de integração",
                priority="high",
                description="Testando workflow completo",
            )
        )

        assert created.id is not None
        assert created.status == "pending"

        # 2. Renomear tarefa
        rename_use_case = RenameTaskUseCase(repository=repository)
        renamed = rename_use_case.execute(
            RenameTaskInput(
                task_id=created.id,
                new_title="Tarefa renomeada",
            )
        )

        assert renamed.old_title == "Tarefa de integração"
        assert renamed.new_title == "Tarefa renomeada"

        # 3. Completar tarefa
        complete_use_case = CompleteTaskUseCase(
            repository=repository,
            clock=clock,
        )
        completed = complete_use_case.execute(CompleteTaskInput(task_id=created.id))

        assert completed.status == "completed"
        assert completed.completed_at is not None

        # 4. Verificar na listagem
        list_use_case = ListTasksUseCase(repository=repository)

        # Lista completas
        completed_list = list_use_case.execute(ListTasksInput(filter=TaskFilter.COMPLETED))
        assert completed_list.total == 1
        assert completed_list.tasks[0].title == "Tarefa renomeada"

        # Lista pendentes (deve estar vazia)
        pending_list = list_use_case.execute(ListTasksInput(filter=TaskFilter.PENDING))
        assert pending_list.total == 0

    @pytest.mark.integration
    def test_cannot_modify_completed_task(
        self,
        repository: InMemoryTaskRepository,
        clock: SystemClock,
        id_generator: UUIDGenerator,
    ) -> None:
        """Verifica que tarefas completadas não podem ser modificadas."""
        # Criar e completar tarefa
        create_use_case = CreateTaskUseCase(
            repository=repository,
            clock=clock,
            id_generator=id_generator,
        )
        created = create_use_case.execute(CreateTaskInput(title="Tarefa"))

        complete_use_case = CompleteTaskUseCase(
            repository=repository,
            clock=clock,
        )
        complete_use_case.execute(CompleteTaskInput(task_id=created.id))

        # Tentar renomear deve falhar
        rename_use_case = RenameTaskUseCase(repository=repository)

        with pytest.raises(BusinessRuleViolationException):
            rename_use_case.execute(RenameTaskInput(task_id=created.id, new_title="Novo título"))

    @pytest.mark.integration
    def test_multiple_tasks_workflow(
        self,
        repository: InMemoryTaskRepository,
        clock: SystemClock,
        id_generator: UUIDGenerator,
    ) -> None:
        """Testa workflow com múltiplas tarefas."""
        create_use_case = CreateTaskUseCase(
            repository=repository,
            clock=clock,
            id_generator=id_generator,
        )

        # Criar várias tarefas
        task_ids: list[str] = []
        for i in range(5):
            output = create_use_case.execute(
                CreateTaskInput(
                    title=f"Tarefa {i + 1}",
                    priority="medium" if i % 2 == 0 else "high",
                )
            )
            task_ids.append(output.id)

        # Completar algumas
        complete_use_case = CompleteTaskUseCase(
            repository=repository,
            clock=clock,
        )
        complete_use_case.execute(CompleteTaskInput(task_id=task_ids[0]))
        complete_use_case.execute(CompleteTaskInput(task_id=task_ids[2]))

        # Verificar listagem
        list_use_case = ListTasksUseCase(repository=repository)

        all_tasks = list_use_case.execute(ListTasksInput(filter=TaskFilter.ALL))
        assert all_tasks.total == 5

        completed_tasks = list_use_case.execute(ListTasksInput(filter=TaskFilter.COMPLETED))
        assert completed_tasks.total == 2

        pending_tasks = list_use_case.execute(ListTasksInput(filter=TaskFilter.PENDING))
        assert pending_tasks.total == 3

    @pytest.mark.integration
    def test_task_persistence(
        self,
        repository: InMemoryTaskRepository,
        clock: SystemClock,
        id_generator: UUIDGenerator,
    ) -> None:
        """Verifica que as mudanças são persistidas corretamente."""
        create_use_case = CreateTaskUseCase(
            repository=repository,
            clock=clock,
            id_generator=id_generator,
        )
        created = create_use_case.execute(CreateTaskInput(title="Tarefa original"))

        # Renomear
        rename_use_case = RenameTaskUseCase(repository=repository)
        rename_use_case.execute(RenameTaskInput(task_id=created.id, new_title="Tarefa modificada"))

        # Verificar que a mudança foi persistida
        list_use_case = ListTasksUseCase(repository=repository)
        tasks = list_use_case.execute(ListTasksInput())

        assert tasks.total == 1
        assert tasks.tasks[0].title == "Tarefa modificada"
