# ADR 0003: Design do Event Dispatcher

## Status

Aceito

## Contexto

Precisamos de um mecanismo para:
- Entidades emitirem eventos de domínio
- Desacoplar produtor e consumidor de eventos
- Permitir múltiplos handlers para o mesmo evento
- Preparar para evolução futura (filas, async)

## Decisão

### 1. Entidades acumulam eventos

```python
class Task(Entity[TaskId]):
    def complete(self, completed_at: datetime) -> None:
        # ... lógica
        self.add_event(TaskCompleted(task_id=self.id.value))
```

### 2. Use Cases coletam e despacham

```python
class CompleteTaskUseCase:
    def execute(self, input: Input) -> Output:
        task.complete(completed_at)
        self._repository.save(task)
        self._dispatcher.dispatch_all(task.clear_events())
```

### 3. Dispatcher na Infrastructure

```python
class EventDispatcher:
    def register(self, event_type, handler): ...
    def dispatch(self, event): ...
    def dispatch_all(self, events): ...
```

## Justificativa

1. **Entidades não conhecem dispatcher**: Apenas acumulam eventos
2. **Use Case controla fluxo**: Decide quando despachar
3. **Dispatcher é infra**: Pode evoluir para RabbitMQ, Kafka, etc.

## Consequências

### Positivas
- Eventos são despachados após persistência (consistência)
- Fácil adicionar handlers sem modificar entidades
- Preparado para async e filas

### Negativas
- Use Case precisa lembrar de despachar eventos
- Eventos em memória podem ser perdidos se app crashar
