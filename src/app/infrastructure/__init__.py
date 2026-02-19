"""
Camada de Infraestrutura (Infrastructure Layer).

Esta camada contém implementações concretas de interfaces definidas
nas camadas internas:
- Persistence: implementações de repositórios (in-memory, SQL, etc.)
- Providers: implementações de serviços (clock, ID generator, etc.)
- Messaging: implementações de mensageria e eventos
- External Services: integrações com serviços externos

REGRAS IMPORTANTES:
1. Esta camada pode depender de todas as outras camadas
2. Implementa as interfaces (ports) definidas na camada de aplicação
3. Contém detalhes de implementação e dependências de frameworks
4. Deve ser facilmente substituível (graças às interfaces)
"""
