# ADR-002: Provider Factory Implementation

**Status:** Concluído  
**Data:** 24/08/2026  
**Fase:** FASE 2.0 — Infraestrutura de AI Providers

---

## Contexto

A FASE 1.0 estabeleceu a fundação do AquaBot com uma abstração básica de provedores de IA (AIProvider) e uma implementação concreta (KimiProvider). No entanto, a seleção do provider estava hardcoded diretamente no código, limitando a flexibilidade do sistema.

## Decisão

Implementar um ProviderFactory para permitir seleção dinâmica de provedores de IA através de configuração, mantendo a arquitetura existente e adicionando um método metadata() ao contrato base.

## Detalhes da Implementação

### 1. ProviderFactory

**Arquivo:** `backend/ai/factory.py`

**Funcionalidades:**
- Criação de providers baseados em configuração
- Registro dinâmico de novos providers
- Validação de providers desconhecidos
- Suporte a case-insensitive selection

**Uso:**
```python
from backend.ai.factory import ProviderFactory

# Usar configuração padrão
provider = ProviderFactory.create()

# Especificar provider explicitamente
provider = ProviderFactory.create("kimi")
```

### 2. Configuração

**Arquivo:** `backend/config.py`

**Nova variável:**
```python
AI_PROVIDER = os.getenv("AI_PROVIDER", "kimi")
```

**Arquivo:** `.env.example`

**Nova configuração:**
```env
AI_PROVIDER=kimi
```

### 3. AIProvider - metadata()

**Arquivo:** `backend/ai/base.py`

**Novo método:**
```python
def metadata(self) -> Dict[str, Any]:
    """Retorna metadados sobre o provider."""
    return {"provider": self.__class__.__name__}
```

**Implementação default:**
- Não obriga providers futuros a implementar informações específicas
- Pode ser sobrescrito por providers concretos
- Não expõe informações sensíveis

### 4. KimiProvider - metadata()

**Arquivo:** `backend/ai/kimi.py`

**Implementação específica:**
```python
def metadata(self) -> Dict[str, Any]:
    return {
        "provider": "KimiProvider",
        "model": self.model,
        "api_configured": bool(self.api_key),
    }
```

**Segurança:**
- `api_configured` retorna apenas booleano
- A chave API nunca é exposta
- Modelo é derivado da configuração

## Justificativa

1. **Flexibilidade:** Permite trocar providers sem alterar código
2. **Testabilidade:** Facilita testes com diferentes providers
3. **Extensibilidade:** Novos providers podem ser registrados dinamicamente
4. **Compatibilidade:** Mantém contratos existentes funcionando
5. **Segurança:** metadata() não expõe secrets

## Consequências

### Positivas
- Sistema preparado para múltiplos providers
- Configuração centralizada de seleção de IA
- Testes cobrem Factory e metadata
- Documentação atualizada

### Negativas
- Leve aumento de complexidade com Factory
- Nova dependência: typing (já parte do Python stdlib)

## Alternativas Consideradas

1. **DI Framework:** Rejeitado por adicionar complexidade desnecessária
2. **Singleton pattern:** Rejeitado por dificultar testes
3. **Configuração hardcoded:** Rejeitado por limitar flexibilidade

## Testes

**Novos testes criados:**
- `test_factory.py` - 8 testes para ProviderFactory
- `test_ai_metadata.py` - 4 testes para metadata()
- `test_ai_service_factory.py` - 2 testes para integração AIService + Factory
- `test_kimi.py` - 1 teste adicional para metadata do KimiProvider

**Total de testes:** 34 (19 anteriores + 15 novos)

**Resultado:** 100% de sucesso

## Migração

Nenhuma migração necessária. A implementação é backward compatible.

## Referências

- Documento Técnico Master - Seção 7 (Provider Interface)
- Documento Técnico Master - Seção 8 (AquaBot Orchestrator)
- ARCHITECTURE.md - Princípios de arquitetura
- PROJECT_RULES.md - Regras do projeto

---

**Responsável:** Devin (Assistente de Engenharia)  
**Aprovado por:** Carlos Gomes (pendente)