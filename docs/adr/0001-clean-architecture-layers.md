# ADR 0001: Clean Architecture com Camadas Bem Definidas

## Status

Aceito

## Contexto

Precisamos de uma arquitetura que:
- Separe claramente responsabilidades
- Permita testes isolados
- Facilite mudanças de tecnologia
- Seja compreensível para novos desenvolvedores

## Decisão

Adotamos **Clean Architecture** com 4 camadas:

```
┌─────────────────────────────────────────┐
│              INTERFACES                  │
│         (CLI, API, Controllers)         │
├─────────────────────────────────────────┤
│            INFRASTRUCTURE                │
│    (Repositories, Providers, DB)        │
├─────────────────────────────────────────┤
│             APPLICATION                  │
│        (Use Cases, Ports, DTOs)         │
├─────────────────────────────────────────┤
│               DOMAIN                     │
│   (Entities, Value Objects, Events)     │
└─────────────────────────────────────────┘
```

### Regra de Dependência

**Dependências sempre apontam para dentro (em direção ao Domain).**

- Domain não importa nada de outras camadas
- Application importa apenas Domain
- Infrastructure implementa interfaces da Application
- Interfaces usa Application e pode usar Infrastructure para DI

## Consequências

### Positivas
- Domain 100% puro, sem dependências externas
- Fácil testar cada camada isoladamente
- Trocar banco de dados não afeta regras de negócio
- Código organizado e previsível

### Negativas
- Mais arquivos e indireção
- Curva de aprendizado inicial
- Pode parecer "over-engineering" para projetos simples

## Referências

- Clean Architecture (Robert C. Martin)
- Hexagonal Architecture (Alistair Cockburn)
