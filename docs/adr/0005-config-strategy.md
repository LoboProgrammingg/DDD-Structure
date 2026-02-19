# ADR 0005: Estratégia de Configuração Centralizada

## Status

Aceito

## Contexto

Configurações espalhadas pelo código causam:
- Dificuldade em encontrar o que configurar
- Valores hardcoded difíceis de mudar
- Comportamento inconsistente entre ambientes

## Decisão

Usamos **Pydantic Settings** com configuração centralizada:

```python
# infrastructure/config/settings.py
class Settings(BaseSettings):
    app_name: str = "DDD Template"
    environment: Environment = Environment.DEVELOPMENT
    log_level: LogLevel = LogLevel.INFO
    database_url: str = "sqlite:///./app.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )
```

### Fontes de Configuração (ordem de precedência)

1. Variáveis de ambiente
2. Arquivo `.env`
3. Valores padrão no código

## Justificativa

1. **Um lugar só**: Todas as configs em `settings.py`
2. **Validação**: Pydantic valida tipos no startup
3. **12-Factor**: Configuração via ambiente
4. **Documentação**: Settings é auto-documentado

## Consequências

### Positivas
- Fail fast: erros de config detectados no startup
- Fácil ver todas as opções disponíveis
- Suporte nativo a `.env` para desenvolvimento
- Type-safe: IDE ajuda com autocomplete

### Negativas
- Dependência do Pydantic (já usamos, então ok)
- Precisa reiniciar app para mudar configs
