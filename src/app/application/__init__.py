"""
Camada de Aplicação (Application Layer).

Esta camada orquestra o fluxo da aplicação e contém:
- Use Cases: implementações dos casos de uso do sistema
- Ports: interfaces (contratos) para serviços externos
- DTOs: objetos de transferência de dados
- Application Services: coordenação de múltiplos use cases

REGRAS IMPORTANTES:
1. Esta camada pode depender apenas da camada de domínio
2. Use Cases recebem ports (interfaces) via injeção de dependência
3. Não deve conter lógica de negócio (isso vai no domínio)
4. Responsável por coordenar e orquestrar operações
5. Despacha eventos de domínio após operações bem-sucedidas
"""
