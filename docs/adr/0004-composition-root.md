# ADR 0004: Composition Root explícito, sem framework de DI

## Status

Aceito

## Contexto

Casos de uso dependem de abstrações (Unit of Work, Clock, NotificationSender).
Alguém precisa escolher e montar as implementações concretas, de preferência
em um único lugar e sem espalhar instanciação pelo código.

## Decisão

`app/bootstrap/container.py` é o **Composition Root**. O `Container` cria
engine, session factory, event bus e todos os handlers, e registra as
inscrições de eventos entre contextos. Fábricas de Unit of Work são
`functools.partial`, então cada chamada de caso de uso abre sua própria
transação.

```python
container = Container(settings, notification_sender=SmtpSender(...))
task_id = await container.create_task(CreateTask(title="Revisar ADRs"))
```

A API recebe o container em `create_app(container)` e o expõe via
`request.app.state`; a CLI cria o seu. Não existe singleton global.

## Consequências

- Todas as dependências do sistema são legíveis em um arquivo.
- Testes montam um container com outro banco ou outros adaptadores sem
  monkeypatch.
- O container cresce com o sistema; quando ficar grande, divida em um
  módulo de wiring por bounded context.

## Alternativas consideradas

- **Bibliotecas de DI** (`dependency-injector`, `punq`): mais mágica e mais
  uma dependência para resolver um problema que construtores já resolvem.
- **`Depends` do FastAPI em toda a cadeia**: acoplaria a aplicação ao
  framework web e deixaria a CLI sem o mesmo wiring.
