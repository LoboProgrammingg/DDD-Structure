"""
Sample Context - Gerenciamento de Tarefas (Task Management).

Este é um bounded context de exemplo que demonstra os padrões DDD.
Implementa um sistema simples de gerenciamento de tarefas (ToDo).

Contém:
- Task: entidade principal
- Value Objects: TaskTitle, TaskDescription, TaskPriority, TaskStatus
- Domain Events: TaskCreated, TaskCompleted, TaskRenamed

NOTA: Interfaces de Repository ficam na camada Application (ports),
não no Domain. O Domain é 100% puro e focado em regras de negócio.
"""
