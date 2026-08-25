# AQUABOT - DOCUMENTAÇÃO DA API

**Versão:** 1.1  
**Status:** Infraestrutura de AI Providers  
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

**Endpoint:** `POST /api/chat` (planejado)

**Descrição:** Envia uma mensagem para o AquaBot e recebe uma resposta.

**Status:** ❌ Não implementado (FASE 3)

**Request Body (planejado):**

```json
{
  "message": "Olá, como você está?",
  "conversation_id": "optional-uuid"
}
```

**Response (planejado):**

```json
{
  "response": "Olá! Estou bem, obrigado. Como posso ajudar você hoje?",
  "conversation_id": "uuid",
  "timestamp": "2026-08-24T23:00:00Z"
}
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

- `500 Internal Server Error` - Erro interno do servidor
- `502 Bad Gateway` - Gateway inválido
- `503 Service Unavailable` - Serviço indisponível
- `504 Gateway Timeout` - Timeout do gateway

---

## 5. FORMATO DE ERROS

### 5.1 Estrutura de Erro

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Descrição do erro",
    "details": "Detalhes adicionais (opcional)"
  }
}
```

### 5.2 Exemplos de Erro

**400 Bad Request:**

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "O campo 'message' é obrigatório"
  }
}
```

**401 Unauthorized:**

```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Token de autenticação inválido"
  }
}
```

**500 Internal Server Error:**

```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "Erro interno do servidor"
  }
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

### 16.1 Versão 1.0 (24/08/2026)

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
**Versão:** 1.0  
**Status:** Fundação Estabilizada  
**Data:** 24/08/2026