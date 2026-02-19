"""
Port para repositório de tarefas na camada de aplicação.

Re-exporta a interface do domínio para uso na aplicação.
Isso mantém a camada de aplicação desacoplada do domínio em termos de imports.
"""

from app.domain.sample_context.repositories.task_repository import TaskRepository


# Alias para uso na camada de aplicação
TaskRepositoryPort = TaskRepository

__all__ = ["TaskRepositoryPort"]
