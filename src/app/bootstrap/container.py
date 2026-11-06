"""Composition Root: o único lugar que conhece as implementações concretas.

Todas as dependências são montadas aqui, de forma explícita e sem framework de
DI. Interfaces (API, CLI) recebem o container pronto; testes podem montar o
seu próprio com outras configurações ou adaptadores.
"""

from functools import partial

from sqlalchemy import text

from app.application.notification.commands import SendNotificationHandler
from app.application.notification.ports import NotificationSender
from app.application.shared import Clock
from app.application.task_management.commands import (
    AssignTaskHandler,
    CancelTaskHandler,
    CompleteTaskHandler,
    CreateTaskHandler,
    RenameTaskHandler,
    ReprioritizeTaskHandler,
    StartTaskHandler,
)
from app.application.task_management.queries import GetTaskHandler, ListTasksHandler
from app.domain.task_management.events import TaskAssigned
from app.domain.task_management.services import WorkInProgressPolicy
from app.infrastructure.config import Settings, get_settings
from app.infrastructure.database import create_engine, create_session_factory
from app.infrastructure.messaging import InProcessEventBus
from app.infrastructure.notification.acl import TaskEventsTranslator
from app.infrastructure.notification.logging_notification_sender import (
    LoggingNotificationSender,
)
from app.infrastructure.providers import SystemClock
from app.infrastructure.read_models import SqlTaskReadModel
from app.infrastructure.unit_of_work import (
    SqlAlchemyNotificationUnitOfWork,
    SqlAlchemyTaskManagementUnitOfWork,
)


class Container:
    def __init__(
        self,
        settings: Settings,
        *,
        clock: Clock | None = None,
        notification_sender: NotificationSender | None = None,
    ) -> None:
        self.settings = settings
        self.engine = create_engine(settings.database_url, echo=settings.database_echo)
        self.session_factory = create_session_factory(self.engine)
        self.event_bus = InProcessEventBus()
        self.clock = clock or SystemClock()

        task_uow = partial(SqlAlchemyTaskManagementUnitOfWork, self.session_factory, self.event_bus)
        notification_uow = partial(
            SqlAlchemyNotificationUnitOfWork, self.session_factory, self.event_bus
        )
        task_read_model = SqlTaskReadModel(self.session_factory)
        wip_policy = WorkInProgressPolicy(limit=settings.work_in_progress_limit)

        self.create_task = CreateTaskHandler(task_uow, self.clock)
        self.rename_task = RenameTaskHandler(task_uow)
        self.reprioritize_task = ReprioritizeTaskHandler(task_uow)
        self.assign_task = AssignTaskHandler(task_uow)
        self.start_task = StartTaskHandler(task_uow, wip_policy)
        self.complete_task = CompleteTaskHandler(task_uow, self.clock)
        self.cancel_task = CancelTaskHandler(task_uow)
        self.get_task = GetTaskHandler(task_read_model)
        self.list_tasks = ListTasksHandler(task_read_model)

        self.send_notification = SendNotificationHandler(
            notification_uow, notification_sender or LoggingNotificationSender(), self.clock
        )

        self._subscribe_event_handlers()

    def _subscribe_event_handlers(self) -> None:
        task_events = TaskEventsTranslator(self.send_notification)
        self.event_bus.subscribe(TaskAssigned, task_events.on_task_assigned)

    async def database_is_reachable(self) -> bool:
        try:
            async with self.engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
        except Exception:
            return False
        return True

    async def dispose(self) -> None:
        await self.engine.dispose()


def build_container(settings: Settings | None = None) -> Container:
    return Container(settings or get_settings())
