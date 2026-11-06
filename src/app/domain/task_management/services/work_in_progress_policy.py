"""Domain Service: limite de trabalho em andamento (WIP) por responsável.

A regra envolve várias tarefas, então não cabe dentro de um único agregado.
O serviço é puro (sem I/O): recebe as tarefas já carregadas pela aplicação.

A verificação não é transacional entre agregados. Em alta concorrência dois
inícios simultâneos podem ultrapassar o limite; o negócio aceita essa janela
(consistência eventual, Vernon regra 4) em vez de travar todas as tarefas.
"""

from collections.abc import Iterable
from dataclasses import dataclass

from app.domain.task_management.aggregates import Task
from app.domain.task_management.exceptions import WorkInProgressLimitExceeded
from app.domain.task_management.specifications import InProgressTask


@dataclass(frozen=True)
class WorkInProgressPolicy:
    limit: int = 3

    def __post_init__(self) -> None:
        if self.limit < 1:
            raise ValueError("O limite de WIP deve ser maior que zero.")

    def start(self, task: Task, assignee_tasks: Iterable[Task]) -> None:
        in_progress = InProgressTask()
        ongoing = sum(
            1 for other in assignee_tasks if other != task and in_progress.is_satisfied_by(other)
        )
        if ongoing >= self.limit:
            raise WorkInProgressLimitExceeded(
                f"O responsável já tem {ongoing} tarefa(s) em andamento (limite: {self.limit})."
            )
        task.start()
