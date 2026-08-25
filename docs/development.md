# AQUABOT - GUIA DE DESENVOLVIMENTO

**Versão:** 1.0  
**Status:** Fundação Estabilizada  
**Data:** 24/08/2026

---

## 1. CONFIGURAÇÃO DO AMBIENTE

### 1.1 Pré-requisitos

- Python 3.14.6 ou superior
- Git
- Ambiente virtual (recomendado)

### 1.2 Configuração Inicial

```bash
# Clone do repositório
git clone <repositório>
cd AquaBot

# Criação do ambiente virtual
python -m venv .venv

# Ativação do ambiente virtual
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Instalação das dependências
pip install -r requirements.txt

# Configuração das variáveis de ambiente
cp .env.example .env
# Edite .env com suas configurações
```

### 1.3 Variáveis de Ambiente

Edite o arquivo `.env` com suas configurações:

```env
APP_NAME=AquaBot
APP_ENV=development
DEBUG=true
SECRET_KEY=sua-chave-secreta-aqui
KIMI_API_KEY=sua-api-key-aqui
KIMI_MODEL=kimi-k2.6
OTHER_AI_API_KEY=
DATABASE_URL=
```

---

## 2. EXECUÇÃO DA APLICAÇÃO

### 2.1 Modo de Desenvolvimento

```bash
# Ativação do ambiente virtual
.venv\Scripts\activate

# Execução da aplicação
python backend/app.py
```

A aplicação estará disponível em `http://127.0.0.1:5000`

### 2.2 Health Check

```bash
# Teste do endpoint de health
curl http://127.0.0.1:5000/health
```

Resposta esperada:
```json
{
  "status": "ok",
  "app": "AquaBot"
}
```

---

## 3. TESTES

### 3.1 Execução de Todos os Testes

```bash
# Usando o ambiente virtual
.venv\Scripts\python.exe -m pytest tests/ -v
```

### 3.2 Execução de Testes Específicos

```bash
# Teste de um arquivo específico
.venv\Scripts\python.exe -m pytest tests/test_ai_base.py -v

# Teste de uma função específica
.venv\Scripts\python.exe -m pytest tests/test_ai_base.py::test_provider -v
```

### 3.3 Cobertura de Testes

```bash
# Execução com cobertura
.venv\Scripts\python.exe -m pytest tests/ --cov=backend --cov-report=html
```

### 3.4 Escrita de Testes

**Padrão recomendado:**

```python
import pytest
from backend.ai.base import AIProvider

class FakeAIProvider(AIProvider):
    def generate(self, prompt: str) -> str:
        return "Resposta simulada"

def test_provider_generates_response():
    provider = FakeAIProvider()
    result = provider.generate("teste")
    assert result == "Resposta simulada"
```

**Regras:**
- Usar mocks/fakes para dependências externas
- Não depender de APIs pagas
- Testar casos de sucesso e erro
- Nomes descritivos para testes

---

## 4. ESTRUTURA DE CÓDIGO

### 4.1 Convenções de Nomenclatura

**Python:**
- Classes: `PascalCase` (ex: `AIProvider`)
- Funções/Métodos: `snake_case` (ex: `generate_response`)
- Variáveis: `snake_case` (ex: `api_key`)
- Constantes: `UPPER_SNAKE_CASE` (ex: `API_URL`)
- Módulos: `snake_case` (ex: `ai_service.py`)

**Arquivos:**
- `snake_case.py` para módulos Python
- `PascalCase.md` para documentos markdown

### 4.2 Organização de Arquivos

**Backend:**
```python
# Importações padrão
import os
import sys

# Importações de terceiros
from flask import Flask
import requests

# Importações locais
from backend.config import Config
from backend.ai.base import AIProvider
```

**Ordem recomendada:**
1. Módulos padrão
2. Módulos de terceiros
3. Módulos locais

### 4.3 Docstrings

**Padrão:**

```python
def generate(self, prompt: str) -> str:
    """
    Gera uma resposta a partir de um prompt.
    
    Args:
        prompt: Texto de entrada para a IA.
    
    Returns:
        Resposta gerada pela IA.
    
    Raises:
        KimiAPIError: Se houver erro na comunicação com a API.
    """
    pass
```

---

## 5. PROVIDER FACTORY

### 5.1 Uso do ProviderFactory

**Criação de provider por configuração:**

```python
from backend.ai.factory import ProviderFactory

# Usar configuração padrão do .env
provider = ProviderFactory.create()

# Especificar provider explicitamente
provider = ProviderFactory.create("kimi")
```

**Registro de novo provider:**

```python
from backend.ai.factory import ProviderFactory
from backend.ai.base import AIProvider

class MyCustomProvider(AIProvider):
    def generate(self, prompt: str) -> str:
        return f"Custom: {prompt}"

ProviderFactory.register_provider("custom", MyCustomProvider)
```

**Tratamento de erros:**

```python
from backend.ai.factory import ProviderFactory, ProviderFactoryError

try:
    provider = ProviderFactory.create("unknown")
except ProviderFactoryError as e:
    print(f"Erro: {e}")
```

### 5.2 Configuração de Provider

**Variável de ambiente:**

```env
AI_PROVIDER=kimi
```

**Valores disponíveis:**
- `kimi` - Provider Kimi (padrão)

---

## 6. LOGGING

### 6.1 Uso do Logger

```python
from backend.core.logging import get_logger

logger = get_logger("AquaBot")

logger.info("Aplicação iniciada")
logger.warning("Configuração não encontrada")
logger.error("Falha na comunicação com API")
```

### 6.2 Regras de Logging

**SEMPRE logar:**
- Inicialização de componentes
- Erros e exceções
- Eventos importantes do negócio
- Mudanças de estado

**NUNCA logar:**
- API keys
- Tokens
- Senhas
- Secrets
- Dados sensíveis de usuários

### 6.3 Níveis de Log

- `DEBUG` - Informações detalhadas para debugging
- `INFO` - Informações gerais de operação
- `WARNING` - Avisos que não impedem operação
- `ERROR` - Erros que requerem atenção
- `CRITICAL` - Erros críticos que impedem operação

---

## 7. GIT

### 7.1 Branches

**Branch principal:** `master`

**Recomendação:**
- Criar branches para features
- Criar branches para correções de bugs
- Manter `master` sempre estável

### 7.2 Commits

**Padrão de mensagens:**

```
feat: adicionar nova funcionalidade
fix: corrigir bug específico
test: adicionar ou atualizar testes
docs: atualizar documentação
refactor: refatorar código sem mudar comportamento
style: mudanças de estilo (formatação, etc.)
chore: tarefas de manutenção
```

**Exemplos:**
```
feat: implementar sistema de logging
fix: corrigir tratamento de erro no KimiClient
test: adicionar testes para AIService
docs: atualizar guia de desenvolvimento
```

### 7.3 Fluxo de Trabalho

```bash
# Verificar status
git status

# Adicionar arquivos
git add <arquivo>

# Commit
git commit -m "mensagem semântica"

# Push
git push origin <branch>
```

---

## 8. DEPENDÊNCIAS

### 8.1 Adição de Dependências

**Procedimento:**

1. Verificar necessidade real
2. Pesquisar alternativas
3. Avaliar compatibilidade
4. Testar em ambiente de desenvolvimento
5. Adicionar ao `requirements.txt` com versão específica
6. Atualizar `.env.example` se necessário
7. Documentar mudança

**Exemplo:**

```bash
# Instalar e testar
pip install sqlalchemy==2.0.0

# Adicionar ao requirements.txt
echo "sqlalchemy==2.0.0" >> requirements.txt

# Commit
git add requirements.txt
git commit -m "deps: adicionar sqlalchemy 2.0.0"
```

### 8.2 Atualização de Dependências

**Procedimento:**

1. Verificar changelog
2. Testar em ambiente de desenvolvimento
3. Executar testes completos
4. Atualizar `requirements.txt`
5. Documentar mudanças

---

## 9. DEBUGGING

### 9.1 Debugging com Python

```python
import pdb

def minha_funcao():
    pdb.set_trace()  # Ponto de parada
    # código para debugar
```

### 9.2 Debugging com Flask

```python
# Em modo de desenvolvimento
app.run(debug=True)
```

### 9.3 Logs de Debug

```python
from backend.core.logging import get_logger

logger = get_logger("AquaBot")
logger.setLevel(logging.DEBUG)  # Nível DEBUG
logger.debug("Variável x = %s", x)
```

---

## 10. SEGURANÇA

### 10.1 Variáveis de Ambiente

**Regras:**
- Nunca commitar `.env`
- Usar `.env.example` como template
- Nunca hardcodear segredos
- Rotacionar chaves periodicamente

### 10.2 Validação de Entrada

**Sempre validar:**
- Inputs de usuários
- Parâmetros de API
- Dados de arquivos
- Headers HTTP

**Exemplo:**

```python
def validate_input(prompt: str) -> bool:
    if not prompt or len(prompt) > 10000:
        return False
    return True
```

### 10.3 Tratamento de Erros

**Não expor detalhes internos:**

```python
try:
    result = api_call()
except Exception as e:
    logger.error("Erro na API: %s", str(e))
    return {"error": "Erro interno"}, 500
```

---

## 11. ARQUITETURA

### 11.1 Princípios

- **Separação de responsabilidades:** Cada módulo tem uma função clara
- **Baixo acoplamento:** Módulos independentes
- **Alta coesão:** Funções relacionadas juntas
- **Injeção de dependências:** Facilita testes
- **Interface sobre implementação:** Usar contratos abstratos

### 11.2 Adição de Novos Componentes

**Passos:**

1. Verificar `ARCHITECTURE.md` e `PROJECT_RULES.md`
2. Identificar local apropriado
3. Criar contrato abstrato se necessário
4. Implementar conforme padrões existentes
5. Criar testes
6. Atualizar documentação
7. Executar testes completos

---

## 12. DOCUMENTAÇÃO

### 12.1 Tipos de Documentação

- `README.md` - Visão geral do projeto
- `ARCHITECTURE.md` - Princípios arquiteturais
- `PROJECT_RULES.md` - Regras do projeto
- `docs/architecture.md` - Detalhes técnicos
- `docs/development.md` - Guia de desenvolvimento (este documento)
- `docs/api.md` - Documentação da API
- `docs/AQUABOT_AUDIT.md` - Relatório de auditoria

### 12.2 Atualização de Documentação

**Quando atualizar:**
- Adicionar nova funcionalidade
- Mudar arquitetura
- Alterar procedimentos
- Corrigir bugs importantes

---

## 13. TROUBLESHOOTING

### 13.1 Problemas Comuns

**Erro: ModuleNotFoundError**

```bash
# Solução: Instalar dependências
pip install -r requirements.txt
```

**Erro: Port already in use**

```bash
# Solução: Mudar porta ou matar processo
python backend/app.py  # Usa porta padrão 5000
# Ou matar processo na porta 5000
```

**Erro: KIMI_API_KEY não configurada**

```bash
# Solução: Configurar .env
echo "KIMI_API_KEY=sua-chave" >> .env
```

### 13.2 Verificação de Saúde

```bash
# Verificar ambiente virtual
.venv\Scripts\python.exe --version

# Verificar dependências
.venv\Scripts\pip.exe list

# Verificar testes
.venv\Scripts\python.exe -m pytest tests/ -v

# Verificar aplicação
python backend/app.py
curl http://127.0.0.1:5000/health
```

---

## 14. BOAS PRÁTICAS

### 14.1 Código Limpo

- Funções pequenas e focadas
- Nomes descritivos
- Evitar duplicação
- Comentários quando necessário
- Type hints quando apropriado

### 13.2 Testes

- Testar antes de commitar
- Cobrir casos de borda
- Usar mocks para dependências externas
- Manter testes rápidos

### 13.3 Git

- Commits pequenos e frequentes
- Mensagens semânticas
- Nunca commitar segredos
- Revisar antes de push

---

## 14. RECURSOS

### 14.1 Documentação Externa

- [Flask Documentation](https://flask.palletsprojects.com/)
- [pytest Documentation](https://docs.pytest.org/)
- [Python Documentation](https://docs.python.org/3.14/)

### 14.2 Documentação Interna

- `ARCHITECTURE.md` - Princípios arquiteturais
- `PROJECT_RULES.md` - Regras do projeto
- `docs/architecture.md` - Detalhes técnicos
- `docs/api.md` - Documentação da API

---

## 15. VERSÃO

**Projeto:** AquaBot  
**Documento:** Development Guide  
**Versão:** 1.1  
**Status:** Infraestrutura de AI Providers  
**Data:** 24/08/2026