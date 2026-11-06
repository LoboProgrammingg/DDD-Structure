# ADR 0005: Configuração centralizada com Pydantic Settings

## Status

Aceito

## Contexto

Configuração espalhada pelo código gera valores fixos difíceis de mudar,
comportamento diferente entre ambientes e falhas descobertas tarde.

## Decisão

`app/infrastructure/config/settings.py` define um único `Settings`
(Pydantic Settings), lido de variáveis de ambiente e, opcionalmente, de `.env`.
Todas as variáveis estão documentadas em `.env.example`.

- Validação no startup: valor inválido derruba a aplicação imediatamente.
- Segredos nunca têm valor padrão de produção nem ficam versionados.
- CORS vem desligado (`cors_origins = []`); origens são explícitas.
- Regras de negócio parametrizáveis (`WORK_IN_PROGRESS_LIMIT`) também passam
  por aqui e chegam ao domínio pelo composition root.

## Consequências

- O domínio e a aplicação nunca leem variáveis de ambiente.
- Testes criam `Settings(...)` com os valores que precisam.

## Alternativas consideradas

- `os.environ` direto: sem validação e sem documentação central.
- Arquivos YAML por ambiente: mais um formato para manter, sem ganho real.
