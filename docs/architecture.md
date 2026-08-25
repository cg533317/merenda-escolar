# AQUABOT - DOCUMENTAÇÃO TÉCNICA DE ARQUITETURA

**Versão:** 1.1  
**Status:** Infraestrutura de AI Providers  
**Data:** 24/08/2026

---

## 1. VISÃO GERAL

Este documento complementa o `ARCHITECTURE.md` com detalhes técnicos específicos da implementação atual do AquaBot. Para princípios arquiteturais e decisões de design, consulte o documento de autoridade `ARCHITECTURE.md`.

---

## 2. ESTRUTURA TÉCNICA ATUAL

### 2.1 Estrutura de Diretórios

```
AquaBot/
│
├── backend/
│   ├── __init__.py
│   ├── app.py              # Flask application factory
│   ├── config.py           # Configuração centralizada
│   │
│   ├── ai/                 # Camada de abstração de IA
│   │   ├── __init__.py
│   │   ├── base.py         # AIProvider (contrato abstrato)
│   │   ├── factory.py      # ProviderFactory (seleção de providers)
│   │   ├── kimi.py         # KimiProvider (implementação)
│   │   ├── kimi_client.py  # Cliente HTTP do Kimi
│   │   └── kimi_errors.py  # Tratamento de erros
│   │
│   ├── core/               # Componentes centrais
│   │   ├── __init__.py
│   │   └── logging.py      # Sistema de logging
│   │
│   ├── routes/             # Rotas da API
│   │   ├── __init__.py
│   │   └── health.py       # Health check endpoint
│   │
│   └── services/           # Serviços de negócio
│       ├── __init__.py
│       ├── ai_service.py   # Serviço de IA
│       └── app_service.py  # Serviço da aplicação
│
├── database/               # Banco de dados (vazio - futuro)
├── frontend/               # Frontend (vazio - futuro)
├── knowledge/              # Base de conhecimento (vazio - futuro)
├── tests/                  # Testes automatizados
├── docs/                   # Documentação técnica
├── .venv/                  # Ambiente virtual Python
├── .env                    # Variáveis de ambiente (local)
├── .env.example            # Template de variáveis de ambiente
├── .gitignore              # Configuração do Git
├── requirements.txt        # Dependências Python
├── README.md               # Documentação básica
├── ARCHITECTURE.md         # Princípios arquiteturais (autoridade)
└── PROJECT_RULES.md        # Regras do projeto (autoridade)
```

---

## 3. ARQUITETURA DE CAMADAS

### 3.1 Camada de Aplicação (Flask)

**Arquivo:** `backend/app.py`

```python
def create_app():
    """Factory pattern para criação da aplicação Flask."""
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(health_bp)
    return app
```

**Responsabilidades:**
- Inicialização do Flask
- Configuração da aplicação
- Registro de blueprints
- Factory pattern para testabilidade

---

### 3.2 Camada de Configuração

**Arquivo:** `backend/config.py`

```python
class Config:
    """Configurações centrais carregadas de variáveis de ambiente."""
    APP_NAME = os.getenv("APP_NAME", "AquaBot")
    APP_ENV = os.getenv("APP_ENV", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    AI_PROVIDER = os.getenv("AI_PROVIDER", "kimi")
    KIMI_API_KEY = os.getenv("KIMI_API_KEY", "")
    KIMI_MODEL = os.getenv("KIMI_MODEL", "kimi-k2.6")
    OTHER_AI_API_KEY = os.getenv("OTHER_AI_API_KEY", "")
    DATABASE_URL = os.getenv("DATABASE_URL", "")
```

**Responsabilidades:**
- Centralização de configurações
- Carregamento de variáveis de ambiente
- Valores padrão para desenvolvimento
- Segurança (sem segredos hardcoded)

---

### 3.3 Camada de Rotas (API)

**Arquivo:** `backend/routes/health.py`

```python
health_bp = Blueprint("health", __name__)

@health_bp.get("/health")
def health():
    return {"status": "ok", "app": "AquaBot"}
```

**Responsabilidades:**
- Definição de endpoints HTTP
- Validação básica de entrada
- Chamada de serviços apropriados
- Formatação de respostas JSON

**Endpoints Atuais:**
- `GET /health` - Health check

---

### 3.4 Camada de Serviços

**Arquivo:** `backend/services/ai_service.py`

```python
class AIService:
    """Serviço intermediário para provedores de IA."""
    
    def __init__(self, provider: AIProvider):
        self.provider = provider
    
    def generate(self, prompt: str) -> str:
        return self.provider.generate(prompt)
```

**Responsabilidades:**
- Regras de negócio
- Coordenação entre componentes
- Abstração de lógica complexa
- Intermediação com outras camadas

---

### 3.5 Camada de IA

#### Contrato Base

**Arquivo:** `backend/ai/base.py`

```python
class AIProvider(ABC):
    """Contrato abstrato para provedores de IA."""
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Gera uma resposta a partir de um prompt."""
        raise NotImplementedError
    
    def metadata(self) -> Dict[str, Any]:
        """Retorna metadados sobre o provider."""
        return {"provider": self.__class__.__name__}
```

#### Provider Factory

**Arquivo:** `backend/ai/factory.py`

```python
class ProviderFactory:
    """Factory para criação de providers de IA baseados em configuração."""
    
    @classmethod
    def create(cls, provider_name: str = None) -> AIProvider:
        """Cria uma instância de provider baseado na configuração."""
        # Implementação factory pattern
```

**Responsabilidades:**
- Seleção dinâmica de providers por configuração
- Centralização da lógica de criação
- Validação de providers desconhecidos
- Registro de novos providers

#### Implementação Kimi

**Arquivo:** `backend/ai/kimi.py`

```python
class KimiProvider(AIProvider):
    """Provedor de IA baseado na API do Kimi."""
    
    def __init__(self, api_key=None, model=None, client=None):
        self.api_key = api_key or Config.KIMI_API_KEY
        self.model = model or Config.KIMI_MODEL
        self.client = client or KimiClient(self.api_key)
    
    def generate(self, prompt: str) -> str:
        if not self.api_key:
            raise KimiAPIError("KIMI_API_KEY não configurada.")
        return self.client.chat(model=self.model, prompt=prompt)
    
    def metadata(self) -> Dict[str, Any]:
        """Retorna metadados específicos do KimiProvider."""
        return {
            "provider": "KimiProvider",
            "model": self.model,
            "api_configured": bool(self.api_key),
        }
```

#### Cliente HTTP

**Arquivo:** `backend/ai/kimi_client.py`

```python
class KimiClient:
    """Cliente HTTP para comunicação com a API do Kimi."""
    
    BASE_URL = "https://api.moonshot.ai/v1"
    
    def chat(self, model: str, prompt: str) -> str:
        # Implementação de comunicação HTTP
```

**Responsabilidades:**
- Abstração de provedores de IA
- Comunicação com APIs externas
- Tratamento de erros específicos
- Injeção de dependências para testes

---

### 3.6 Camada de Core

**Arquivo:** `backend/core/logging.py`

```python
def setup_logging(name: str = "AquaBot", level: int = logging.INFO) -> logging.Logger:
    """Configura e retorna um logger para o AquaBot."""
    # Implementação de logging

def get_logger(name: str = "AquaBot") -> logging.Logger:
    """Retorna um logger existente ou cria um novo."""
    # Implementação de caching de loggers
```

**Responsabilidades:**
- Logging estruturado
- Configuração centralizada
- Caching de loggers
- Formatação de logs

---

## 4. FLUXO DE DADOS

### 4.1 Fluxo Atual (Health Check)

```
Cliente HTTP
    ↓
GET /health
    ↓
Flask Router
    ↓
health_bp Blueprint
    ↓
health() function
    ↓
JSON Response
```

### 4.2 Fluxo de Criação de Provider (ProviderFactory)

```
Configuração (.env)
    ↓
AI_PROVIDER=kimi
    ↓
ProviderFactory.create()
    ↓
KimiProvider (instância)
    ↓
AIService
    ↓
Uso pela aplicação
```

### 4.3 Fluxo Futuro (Chat - Planejado)

```
Cliente HTTP
    ↓
POST /api/chat
    ↓
Flask Router
    ↓
chat_bp Blueprint
    ↓
ChatRoute
    ↓
ChatService
    ↓
AquaBot Orchestrator (futuro)
    ↓
AIService
    ↓
AIProvider (Kimi/OpenAI/etc)
    ↓
External API
    ↓
Response Processing
    ↓
JSON Response
```

---

## 5. DEPENDÊNCIAS

### 5.1 Dependências Atuais

**requirements.txt:**
```
Flask==3.1.3           # Framework web
python-dotenv==1.2.3   # Variáveis de ambiente
requests==2.34.2       # Cliente HTTP
pytest==9.1.1          # Framework de testes
```

### 5.2 Dependências Indiretas

Instaladas automaticamente:
- `blinker==1.9.0` - Sinalização do Flask
- `click==8.4.2` - CLI do Flask
- `itsdangerous==2.2.0` - Segurança de dados
- `Jinja2==3.1.6` - Templates do Flask
- `MarkupSafe==3.0.3` - Escapamento seguro
- `Werkzeug==3.1.8` - WSGI toolkit
- `certifi==2026.7.22` - Certificados SSL
- `charset-normalizer==3.5.1` - Normalização de charset
- `idna==3.19` - IDNA (Internationalized Domain Names)
- `urllib3==2.7.0` - Cliente HTTP (dependência do requests)
- `colorama==0.4.6` - Cores no terminal
- `iniconfig==2.3.0` - Configuração
- `packaging==26.3` - Empacotamento
- `pluggy==1.6.0` - Plugin system do pytest
- `Pygments==2.21.0` - Syntax highlighting

---

## 6. TESTES

### 6.1 Estrutura de Testes

```
tests/
├── __init__.py
├── test_ai_base.py          # Testes do AIProvider
├── test_ai_metadata.py      # Testes do metadata do AIProvider
├── test_ai_service.py       # Testes do AIService
├── test_ai_service_factory.py # Testes da integração AIService + Factory
├── test_app.py              # Testes da aplicação Flask
├── test_app_service.py      # Testes do AppService
├── test_factory.py          # Testes do ProviderFactory
├── test_kimi.py             # Testes do KimiProvider
├── test_kimi_client.py      # Testes do KimiClient
└── test_logging.py          # Testes do sistema de logging
```

### 6.2 Cobertura Atual

- **Total de testes:** 34
- **Testes unitários:** 34
- **Testes de integração:** 0
- **Cobertura de componentes principais:** 100%

### 6.3 Padrões de Teste

**Uso de Mocks/Fakes:**
```python
class FakeAIProvider(AIProvider):
    def generate(self, prompt: str) -> str:
        return "Resposta simulada"
```

**Injeção de Dependências:**
```python
provider = KimiProvider(
    api_key="test-key",
    client=fake_client  # Mock do cliente HTTP
)
```

---

## 7. LOGGING

### 7.1 Configuração

**Arquivo:** `backend/core/logging.py`

**Níveis de Log:**
- `INFO` - Informações gerais
- `WARNING` - Avisos
- `ERROR` - Erros

**Formato:**
```
[AquaBot] INFO - Mensagem informativa
[AquaBot] WARNING - Aviso
[AquaBot] ERROR - Erro ocorreu
```

### 7.2 Uso

```python
from backend.core.logging import get_logger

logger = get_logger("AquaBot")
logger.info("Aplicação iniciada")
logger.warning("Configuração não encontrada")
logger.error("Falha na comunicação com API")
```

### 7.3 Regras de Segurança

**NUNCA logar:**
- API keys
- Tokens
- Senhas
- Secrets
- Credenciais
- Dados sensíveis de usuários

---

## 8. SEGURANÇA

### 8.1 Configuração de Segurança

**Variáveis de Ambiente:**
- `SECRET_KEY` - Chave secreta da aplicação
- `KIMI_API_KEY` - API key do Kimi
- `OTHER_AI_API_KEY` - API key de outros provedores
- `DATABASE_URL` - URL do banco de dados

**Proteções:**
- `.env` no `.gitignore`
- `.env.example` sem valores reais
- Nenhum segredo no código
- Validação de entrada básica

### 8.2 Práticas de Segurança

✅ **Implementado:**
- Variáveis de ambiente para segredos
- `.gitignore` configurado
- Validação de API keys
- Tratamento de erros sem exposição de detalhes

⚠️ **Pendente (fases futuras):**
- Validação de entrada robusta
- Rate limiting
- CORS configuration
- Headers de segurança
- Autenticação/autorização
- Criptografia de dados sensíveis

---

## 9. DESEMPENHO

### 9.1 Considerações Atuais

- **Framework:** Flask (síncrono)
- **Cliente HTTP:** requests (síncrono)
- **Logging:** Síncrono (stdout)

### 9.2 Considerações Futuras

⚠️ **Pendente (fases futuras):**
- Async/await para I/O bound operations
- Connection pooling
- Caching
- Rate limiting
- Monitoramento de performance

---

## 10. COMPATIBILIDADE

### 10.1 Python

**Versão Atual:** Python 3.14.6

**Compatibilidade:**
- Flask 3.1.3 ✅
- pytest 9.1.1 ✅
- python-dotenv 1.2.3 ✅
- requests 2.34.2 ✅

### 10.2 Sistema Operacional

**Testado em:**
- Windows (ambiente de desenvolvimento atual)

**Planejado:**
- Linux (produção)
- macOS (desenvolvimento alternativo)

---

## 11. EVOLUÇÃO DA ARQUITETURA

### 11.1 Componentes Planejados

**Backend:**
- `backend/api/schemas/` - Validação de dados
- `backend/repositories/` - Acesso a dados
- `backend/core/security.py` - Segurança centralizada

**AI:**
- `backend/ai/factory.py` - Factory de providers
- `backend/ai/prompts/` - Gerenciamento de prompts
- `backend/ai/providers/openai.py` - Provider OpenAI
- `backend/ai/providers/gemini.py` - Provider Gemini

**Services:**
- `backend/services/chat_service.py` - Serviço de chat
- `backend/services/memory_service.py` - Serviço de memória
- `backend/services/knowledge_service.py` - Serviço de conhecimento

---

## 12. DECISÕES ARQUITETURAIS

### 12.1 Flask vs Django

**Decisão:** Flask

**Justificativa:**
- Menos opinião, mais flexibilidade
- Curva de aprendizado menor
- Adequado para API REST
- Melhor para microserviços

### 12.2 Requests vs httpx

**Decisão:** requests

**Justificativa:**
- Biblioteca estabelecida e madura
- Documentação extensa
- Compatibilidade com Python 3.14
- Suficiente para requisitos atuais

### 12.3 python-dotenv vs python-decouple

**Decisão:** python-dotenv

**Justificativa:**
- Padrão da indústria
- Simples e direto
- Integração nativa com Flask

---

## 13. REFERÊNCIAS

### 13.1 Documentos de Autoridade

- `ARCHITECTURE.md` - Princípios arquiteturais
- `PROJECT_RULES.md` - Regras do projeto
- `README.md` - Documentação básica

### 13.2 Documentação Técnica

- `docs/architecture.md` - Este documento
- `docs/development.md` - Guia de desenvolvimento
- `docs/api.md` - Documentação da API
- `docs/AQUABOT_AUDIT.md` - Relatório de auditoria

---

## 14. MANUTENÇÃO

### 14.1 Atualização de Dependências

**Procedimento:**
1. Testar em ambiente de desenvolvimento
2. Verificar compatibilidade
3. Atualizar `requirements.txt`
4. Executar testes completos
5. Documentar mudanças

### 14.2 Adição de Novos Componentes

**Procedimento:**
1. Seguir estrutura existente
2. Criar testes apropriados
3. Atualizar documentação
4. Respeitar princípios do ARCHITECTURE.md
5. Seguir regras do PROJECT_RULES.md

---

## 15. VERSÃO

**Projeto:** AquaBot  
**Documento:** Technical Architecture  
**Versão:** 1.1  
**Status:** Infraestrutura de AI Providers  
**Data:** 24/08/2026