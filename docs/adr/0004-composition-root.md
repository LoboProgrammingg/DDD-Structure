# ADR 0004: Composition Root para Injeção de Dependências

## Status

Aceito

## Contexto

Precisamos de um padrão para:
- Criar e conectar dependências
- Evitar "new" espalhado pelo código
- Facilitar testes com mocks/fakes
- Documentar todas as dependências

## Decisão

Implementamos um **Composition Root** em `bootstrap/container.py`:

```python
@dataclass
class Container:
    settings: Settings

    @cached_property
    def task_repository(self) -> TaskRepository:
        return InMemoryTaskRepository()

    @cached_property
    def create_task_use_case(self) -> CreateTaskUseCase:
        return CreateTaskUseCase(
            repository=self.task_repository,
            clock=self.clock,
            id_generator=self.id_generator,
        )
```

### Características

1. **Único ponto de criação**: Todas as dependências aqui
2. **Lazy loading**: `@cached_property` cria sob demanda
3. **Singleton por padrão**: Mesma instância reutilizada
4. **Configurável**: Recebe Settings para adaptar comportamento

## Justificativa

- **Simplicidade**: Não precisa de framework de DI complexo
- **Explícito**: Fácil ver todas as dependências
- **Testável**: Crie um container diferente para testes
- **Python idiomático**: Usa features nativas da linguagem

## Consequências

### Positivas
- Zero dependências externas para DI
- Código explícito e fácil de debugar
- Fácil substituir implementações

### Negativas
- Container pode crescer muito em projetos grandes
- Sem auto-wiring (precisa configurar manualmente)

## Alternativas Consideradas

- **dependency-injector**: Rejeitado por complexidade
- **FastAPI Depends**: Específico demais para um caso
- **Configuração manual em cada arquivo**: Rejeitado por espalhamento
