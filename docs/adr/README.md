# Architecture Decision Records

Cada decisão arquitetural relevante fica registrada aqui, com contexto,
alternativas e consequências. ADRs não são apagados: quando uma decisão muda,
o ADR antigo é marcado como substituído e aponta para o novo.

| ADR | Decisão | Status |
|-----|---------|--------|
| [0001](0001-clean-architecture-layers.md) | Arquitetura em camadas (Evans) com regra de dependência | Aceito |
| [0002](0002-repositories-in-application-layer.md) | Contratos de repositório na camada de aplicação | Substituído por 0006 |
| [0003](0003-event-dispatcher-design.md) | Event dispatcher chamado pelos casos de uso | Substituído por 0007 |
| [0004](0004-composition-root.md) | Composition Root explícito, sem framework de DI | Aceito |
| [0005](0005-config-strategy.md) | Configuração centralizada com Pydantic Settings | Aceito |
| [0006](0006-repository-contracts-in-domain.md) | Contratos de repositório no domínio | Aceito |
| [0007](0007-unit-of-work-and-post-commit-events.md) | Unit of Work e publicação de eventos após o commit | Aceito |
| [0008](0008-sqlalchemy-explicit-mapping-optimistic-locking.md) | SQLAlchemy com mapeamento explícito e concorrência otimista | Aceito |
| [0009](0009-architecture-contracts-import-linter.md) | Contratos de arquitetura verificados pelo import-linter | Aceito |
| [0010](0010-cqrs-read-model.md) | Lado de leitura separado (CQRS-lite) | Aceito |
