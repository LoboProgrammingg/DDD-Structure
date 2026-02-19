# ADR 0002: Interfaces de Repository na Camada Application

## Status

Aceito

## Contexto

Em muitas implementações de DDD, as interfaces de Repository ficam no Domain.
Porém, isso cria uma dependência conceitual: o Domain passa a "conhecer" persistência.

## Decisão

**Interfaces de Repository ficam na camada Application (como Ports).**

```
application/
  sample_context/
    ports/
      repositories.py  ← Interface TaskRepository aqui
```

O Domain contém apenas:
- Entidades
- Value Objects
- Domain Events
- Domain Services
- Regras de negócio puras

## Justificativa

1. **Domain mais puro**: Entidades não sabem que serão persistidas
2. **Ports & Adapters**: Repository é um "driven port" da aplicação
3. **Testabilidade**: Mais claro onde mockar
4. **Separação**: Domain = regras, Application = orquestração

## Consequências

### Positivas
- Domain 100% focado em regras de negócio
- Fica claro que Repository é uma abstração de infraestrutura
- Segue o padrão Ports & Adapters mais estritamente

### Negativas
- Diferente da abordagem "clássica" de alguns livros de DDD
- Pode confundir quem vem de outras implementações

## Alternativa Considerada

Manter interfaces no Domain (abordagem clássica). Rejeitada porque:
- Acopla Domain ao conceito de persistência
- Viola a ideia de Domain ser framework-agnostic
