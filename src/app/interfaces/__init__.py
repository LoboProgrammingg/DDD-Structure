"""
Camada de Interfaces (Interface Adapters Layer).

Esta camada contém os adaptadores que conectam o mundo externo
com a aplicação:
- CLI: interface de linha de comando
- API: endpoints REST/GraphQL
- Web: controllers para aplicações web
- Consumers: consumers de filas/eventos

REGRAS IMPORTANTES:
1. Esta camada adapta dados externos para o formato interno
2. Converte DTOs/requests em comandos para use cases
3. Não deve conter lógica de negócio
4. Responsável por autenticação, autorização e validação de entrada
"""
