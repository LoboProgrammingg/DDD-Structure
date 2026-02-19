"""
Billing Context - Bounded Context para faturamento.

Este é um bounded context placeholder para demonstrar
como organizar múltiplos contextos no mesmo projeto.

Para implementar este contexto, crie:
- entities/: Invoice, LineItem, etc.
- value_objects/: InvoiceId, Money, etc.
- events/: InvoiceCreated, InvoicePaid, etc.
- services/: PricingService, etc.

Lembre-se:
- Cada contexto tem sua própria linguagem ubíqua
- Contextos se comunicam via eventos ou ACL (Anti-Corruption Layer)
- Não compartilhe entidades entre contextos
"""
