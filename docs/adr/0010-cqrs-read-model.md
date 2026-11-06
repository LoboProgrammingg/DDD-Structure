# ADR 0010: Lado de leitura separado (CQRS-lite)

## Status

Aceito

## Contexto

Agregados existem para proteger invariantes em escritas. Usá-los para
listagens obriga a reconstituir objetos inteiros só para devolver JSON e
empurra preocupações de tela (filtros, paginação) para dentro do repositório.

## Decisão

- **Commands** (`application/<contexto>/commands/`) carregam agregados pelo
  repositório, executam comportamento e fazem commit.
- **Queries** (`application/<contexto>/queries/`) usam uma porta de leitura
  (`TaskReadModel`) que devolve DTOs. A implementação SQL
  (`infrastructure/read_models/`) consulta as tabelas diretamente.
- Mesmo banco e mesmas tabelas: não há projeções assíncronas nem banco de
  leitura separado.

## Consequências

- Listagens com filtro e paginação não tocam o modelo de domínio.
- Se a leitura precisar escalar à parte, a porta já permite trocar a
  implementação por uma projeção alimentada por eventos.
