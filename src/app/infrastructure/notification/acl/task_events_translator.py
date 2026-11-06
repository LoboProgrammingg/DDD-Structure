"""Anti-Corruption Layer entre Task Management (upstream) e Notification (downstream).

O contexto Notification não conhece tarefas. Esta camada consome a Published
Language do upstream (eventos com tipos primitivos) e a traduz para a
linguagem do downstream (o comando ``SendNotification``). Se o modelo de
Task Management mudar, apenas este tradutor precisa acompanhar.
"""

from app.application.notification.commands import SendNotification, SendNotificationHandler
from app.domain.task_management.events import TaskAssigned


class TaskEventsTranslator:
    def __init__(self, send_notification: SendNotificationHandler) -> None:
        self._send_notification = send_notification

    async def on_task_assigned(self, event: TaskAssigned) -> None:
        await self._send_notification(
            SendNotification(
                recipient=event.assignee_id,
                message=f'Você é o novo responsável pela tarefa "{event.title}".',
            )
        )
