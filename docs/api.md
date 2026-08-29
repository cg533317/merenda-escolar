# AQUABOT - DOCUMENTAÇÃO DA API

**Versão:** 1.2  
**Status:** Runtime Integration + Chat API  
**Data:** 24/08/2026

---

## 1. VISÃO GERAL

A API do AquaBot é uma interface RESTful baseada em Flask que fornece endpoints para interação com o assistente inteligente da Escola de Informática Aquarius.

**Base URL:** `http://127.0.0.1:5000`

**Content-Type:** `application/json`

---

## 2. ENDPOINTS

### 2.1 Health Check

Verifica se a API está funcionando corretamente.

**Endpoint:** `GET /health`

**Descrição:** Retorna o status da aplicação.

**Autenticação:** Não requerida

**Parâmetros:** Nenhum

**Resposta de Sucesso:**

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "ok",
  "app": "AquaBot"
}
```

**Códigos de Status:**
- `200 OK` - API funcionando corretamente

**Exemplo de Requisição:**

```bash
curl -X GET http://127.0.0.1:5000/health
```

**Exemplo em Python:**

```python
import requests

response = requests.get("http://127.0.0.1:5000/health")
data = response.json()
print(data)  # {'status': 'ok', 'app': 'AquaBot'}
```

---

## 3. ENDPOINTS FUTUROS (PLANEJADOS)

### 3.1 Chat

**Endpoint:** `POST /api/chat`

**Descrição:** Envia uma mensagem para o AquaBot e recebe uma resposta.

**Status:** ✅ Implementado (FASE 3.0)

**Request Body:**

```json
{
  "message": "Olá, como você está?",
  "model": "kimi-k2.6"
}
```

**Parâmetros:**
- `message` (obrigatório): String com a mensagem do usuário. Máximo 10.000 caracteres.
- `model` (opcional): String com o modelo a ser usado. Se não fornecido, usa o valor de `KIMI_MODEL`. Se fornecido, deve ser exatamente igual ao modelo configurado.

**Response de Sucesso:**

```json
{
  "response": "Olá! Estou bem, obrigado. Como posso ajudar você hoje?",
  "provider": "KimiProvider",
  "model": "kimi-k2.6",
  "timestamp": "2026-08-24T23:00:00Z"
}
```

**Códigos de Status:**
- `200 OK` - Requisição bem-sucedida
- `400 Bad Request` - Erro de validação (message ausente, vazio, muito longo, ou model inválido)
- `500 Internal Server Error` - Erro interno ou configuração ausente
- `502 Bad Gateway` - Erro do provedor de IA

**Exemplo de Requisição:**

```bash
curl -X POST http://127.0.0.1:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá AquaBot"}'
```

**Exemplo em Python:**

```python
import requests

response = requests.post(
    "http://127.0.0.1:5000/api/chat",
    json={"message": "Olá AquaBot"}
)
data = response.json()
print(data["response"])
```

### 3.2 Conversations

**Endpoint:** `GET /api/conversations` (planejado)

**Descrição:** Lista todas as conversas do usuário.

**Status:** ❌ Não implementado (FASE 4)

**Response (planejado):**

```json
{
  "conversations": [
    {
      "id": "uuid",
      "title": "Conversa sobre Excel",
      "created_at": "2026-08-24T23:00:00Z",
      "updated_at": "2026-08-24T23:30:00Z"
    }
  ]
}
```

### 3.3 Conversation Details

**Endpoint:** `GET /api/conversations/{id}` (planejado)

**Descrição:** Retorna detalhes de uma conversa específica.

**Status:** ❌ Não implementado (FASE 4)

**Response (planejado):**

```json
{
  "id": "uuid",
  "title": "Conversa sobre Excel",
  "messages": [
    {
      "role": "user",
      "content": "O que é Excel?",
      "timestamp": "2026-08-24T23:00:00Z"
    },
    {
      "role": "assistant",
      "content": "Excel é um programa de planilhas...",
      "timestamp": "2026-08-24T23:00:05Z"
    }
  ],
  "created_at": "2026-08-24T23:00:00Z",
  "updated_at": "2026-08-24T23:30:00Z"
}
```

### 3.4 Knowledge Search

**Endpoint:** `POST /api/knowledge/search` (planejado)

**Descrição:** Busca na base de conhecimento do AquaBot.

**Status:** ❌ Não implementado (FASE 6)

**Request Body (planejado):**

```json
{
  "query": "função SE no Excel",
  "limit": 5
}
```

**Response (planejado):**

```json
{
  "results": [
    {
      "title": "Função SE no Excel",
      "content": "A função SE é usada para testar condições...",
      "relevance": 0.95
    }
  ]
}
```

---

## 4. CÓDIGOS DE STATUS

### 4.1 Respostas de Sucesso

- `200 OK` - Requisição bem-sucedida
- `201 Created` - Recurso criado com sucesso
- `204 No Content` - Requisição bem-sucedida sem conteúdo

### 4.2 Respostas de Erro do Cliente

- `400 Bad Request` - Requisição malformada
- `401 Unauthorized` - Autenticação necessária
- `403 Forbidden` - Permissão insuficiente
- `404 Not Found` - Recurso não encontrado
- `429 Too Many Requests` - Muitas requisições (rate limiting)

### 4.3 Respostas de Erro do Servidor

- `500 Internal Server Error` - Erro interno do servidor ou configuração ausente
- `502 Bad Gateway` - Erro do provedor de IA
- `503 Service Unavailable` - Serviço indisponível (não implementado)
- `504 Gateway Timeout` - Timeout do gateway (não implementado)

---

## 5. FORMATO DE ERROS

### 5.1 Estrutura de Erro (FASE 3.0)

```json
{
  "error": "error_type",
  "message": "Descrição do erro"
}
```

**Tipos de erro:**
- `validation_error` - Erro de validação de entrada
- `internal_error` - Erro interno do servidor
- `provider_error` - Erro do provedor de IA

### 5.2 Exemplos de Erro

**400 Bad Request (validation_error):**

```json
{
  "error": "validation_error",
  "message": "O campo 'message' é obrigatório."
}
```

**500 Internal Server Error (internal_error):**

```json
{
  "error": "internal_error",
  "message": "Erro interno do servidor."
}
```

**502 Bad Gateway (provider_error):**

```json
{
  "error": "provider_error",
  "message": "Não foi possível obter resposta do provedor de IA."
}
```

---

## 6. AUTENTICAÇÃO

**Status:** ❌ Não implementado (fases futuras)

**Planejado:**

- JWT (JSON Web Tokens)
- Bearer Token authentication
- Refresh tokens

**Exemplo futuro:**

```http
Authorization: Bearer <token>
```

---

## 7. RATE LIMITING

**Status:** ❌ Não implementado (fases futuras)

**Planejado:**

- Limite de requisições por minuto
- Limite de requisições por dia
- Headers de rate limit

**Headers futuros:**

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1632464000
```

---

## 8. CORS

**Status:** ❌ Não configurado (fases futuras)

**Planejado:**

- Configuração de origens permitidas
- Headers CORS apropriados
- Suporte a preflight requests

---

## 9. VALIDAÇÃO

**Status:** ❌ Não implementado (fases futuras)

**Planejado:**

- Validação de request body
- Validação de parâmetros
- Validação de tipos
- Sanitização de inputs

---

## 10. VERSIONAMENTO

**Versão Atual:** 1.0

**Estrutura de versionamento:** SemVer (Major.Minor.Patch)

- **Major:** Mudanças incompatíveis na API
- **Minor:** Funcionalidades adicionadas de forma compatível
- **Patch:** Correções de bugs compatíveis

**Exemplo futuro:**

```http
API-Version: 1.0
```

ou

```http
http://127.0.0.1:5000/api/v1/chat
```

---

## 11. TESTING

### 11.1 Teste de Health Check

```bash
curl -X GET http://127.0.0.1:5000/health
```

### 11.2 Teste com Python

```python
import requests

response = requests.get("http://127.0.0.1:5000/health")
assert response.status_code == 200
data = response.json()
assert data["status"] == "ok"
assert data["app"] == "AquaBot"
```

### 11.3 Teste Automatizado

**Arquivo:** `tests/test_app.py`

```python
from backend.app import app

def test_health_route():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["app"] == "AquaBot"
```

---

## 12. SEGURANÇA

### 12.1 Práticas de Segurança Atuais

✅ **Implementado:**
- Variáveis de ambiente para segredos
- Validação básica de inputs
- Tratamento de erros sem exposição de detalhes

⚠️ **Pendente (fases futuras):**
- Autenticação/autorização
- Rate limiting
- CORS configuration
- Headers de segurança
- Validação robusta de inputs
- Sanitização de dados

### 12.2 Headers de Segurança Futuros

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
```

---

## 13. MONITORAMENTO

**Status:** ❌ Não implementado (fases futuras)

**Planejado:**

- Logging estruturado
- Métricas de performance
- Monitoramento de erros
- Alertas automáticos

---

## 14. DOCUMENTAÇÃO DE REFERÊNCIA

### 14.1 OpenAPI/Swagger

**Status:** ❌ Não implementado (fases futuras)

**Planejado:**

- Especificação OpenAPI 3.0
- Interface Swagger UI
- Geração automática de clientes

### 14.2 Exemplo Futuro de OpenAPI

```yaml
openapi: 3.0.0
info:
  title: AquaBot API
  version: 1.0.0
paths:
  /health:
    get:
      summary: Health check
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                  app:
                    type: string
```

---

## 15. EXEMPLOS DE USO

### 15.1 cURL

```bash
# Health check
curl -X GET http://127.0.0.1:5000/health

# Com headers (futuro)
curl -X POST http://127.0.0.1:5000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"message": "Olá"}'
```

### 15.2 Python

```python
import requests

# Health check
response = requests.get("http://127.0.0.1:5000/health")
print(response.json())

# Chat (futuro)
response = requests.post(
    "http://127.0.0.1:5000/api/chat",
    json={"message": "Olá"},
    headers={"Authorization": "Bearer <token>"}
)
print(response.json())
```

### 15.3 JavaScript

```javascript
// Health check
fetch('http://127.0.0.1:5000/health')
  .then(response => response.json())
  .then(data => console.log(data));

// Chat (futuro)
fetch('http://127.0.0.1:5000/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <token>'
  },
  body: JSON.stringify({ message: 'Olá' })
})
  .then(response => response.json())
  .then(data => console.log(data));
```

---

## 16. MUDANÇAS RECENTES

### 16.1 Versão 1.2 (24/08/2026) - FASE 3.0

**Adicionado:**
- Endpoint `POST /api/chat`
- Configuração `CHAT_MAX_MESSAGE_LENGTH`
- ChatService (backend/services/chat_service.py)
- Rota /api/chat (backend/routes/chat.py)
- Testes do ChatService (tests/test_chat_service.py)
- Testes da rota (tests/test_chat_route.py)
- Composition root em app.py
- Tratamento de erros (400, 500, 502)
- Timestamp em respostas

**Alterado:**
- backend/app.py - Implementado composition root
- backend/config.py - Adicionado CHAT_MAX_MESSAGE_LENGTH
- .env.example - Adicionado CHAT_MAX_MESSAGE_LENGTH

**Removido:**
- Nenhuma remoção

### 16.2 Versão 1.1 (24/08/2026) - FASE 2.0

**Adicionado:**
- ProviderFactory
- Metadata de providers
- Integração Factory + AIService
- Testes de Factory

**Alterado:**
- Nenhuma alteração

**Removido:**
- Nenhuma remoção

### 16.3 Versão 1.0 (24/08/2026) - FASE 1.0

**Adicionado:**
- Endpoint `GET /health`
- Estrutura básica da API
- Documentação inicial

**Alterado:**
- Nenhuma alteração

**Removido:**
- Nenhuma remoção

---

## 17. ROADMAP

### 17.1 Curto Prazo (FASES 2-3)

- Endpoint `POST /api/chat`
- Validação de inputs
- Tratamento robusto de erros

### 17.2 Médio Prazo (FASES 4-6)

- Endpoints de conversas
- Endpoint de busca de conhecimento
- Autenticação JWT
- Rate limiting

### 17.3 Longo Prazo (FASES 7+)

- WebSockets para streaming
- Webhooks para eventos
- API de administração
- Integrações externas

---

## 18. SUPORTE

### 18.1 Problemas Comuns

**Erro: Connection refused**

```bash
# Verificar se a aplicação está rodando
python backend/app.py
```

**Erro: 404 Not Found**

```bash
# Verificar o endpoint correto
curl http://127.0.0.1:5000/health  # Correto
curl http://127.0.0.1:5000/api/health  # Incorreto (ainda não implementado)
```

### 18.2 Contato

Para problemas ou dúvidas sobre a API, consulte:
- `docs/development.md` - Guia de desenvolvimento
- `docs/architecture.md` - Detalhes técnicos
- `PROJECT_RULES.md` - Regras do projeto

---

## 19. VERSÃO

**Projeto:** AquaBot  
**Documento:** API Documentation  
**Versão:** 1.2  
**Status:** Runtime Integration + Chat API  
**Data:** 24/08/2026