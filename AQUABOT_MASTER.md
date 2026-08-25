# AQUABOT MASTER
## Documento Mestre de Continuidade, Arquitetura e Desenvolvimento

**Projeto:** AquaBot  
**Instituição:** Escola de Informática Aquarius  
**Responsável pelo projeto:** Carlos Gomes  
**Status:** Em desenvolvimento ativo  
**Documento:** Master Technical Specification  
**Versão:** 1.0  
**Data:** 24/08/2026

---

# 1. PROPÓSITO DESTE DOCUMENTO

Este documento é a principal referência de continuidade do projeto AquaBot.

Qualquer agente de desenvolvimento que assumir o projeto deverá:

1. Ler este documento antes de modificar qualquer código.
2. Ler `PROJECT_RULES.md`.
3. Ler `ARCHITECTURE.md`.
4. Verificar o estado atual do Git.
5. Verificar os testes existentes.
6. Confirmar o estado real do código antes de executar qualquer plano descrito aqui.

Este documento descreve:

- objetivo do AquaBot;
- arquitetura;
- tecnologias;
- estrutura do projeto;
- estado das fases;
- regras de desenvolvimento;
- regras de segurança;
- estratégia de testes;
- roadmap;
- critérios de aceite;
- comportamento esperado dos agentes de desenvolvimento.

---

# 2. VISÃO DO AQUABOT

O AquaBot é o projeto de inteligência artificial da Escola de Informática Aquarius.

O objetivo é construir progressivamente um assistente de IA próprio, modular, extensível e integrado ao ecossistema tecnológico da Aquarius.

O AquaBot não deve ser tratado simplesmente como:

> "uma interface para uma API de IA".

A visão do projeto é construir uma plataforma composta por diferentes camadas:

```text
                    AQUABOT
                       │
                       ▼
                Interface / API
                       │
                       ▼
                 Chat Core
                       │
                       ▼
              AquaBot Orchestrator
                 │          │
                 │          └──────────────┐
                 ▼                         ▼
             AIService                Context Manager
                 │                         │
                 ▼                         ▼
           ProviderFactory            Memory
                 │                         │
                 ▼                         ▼
          AI Provider(s)              Knowledge
                 │                         │
                 ▼                         ▼
              Kimi API                 RAG
```

Essa arquitetura será construída gradualmente.  
Não implementar todas as camadas simultaneamente.

---

# 3. PRINCÍPIOS FUNDAMENTAIS

O desenvolvimento do AquaBot deve seguir estes princípios:

**Estabilidade**  
    > **Simplicidade**  
    > **Testabilidade**  
    > **Segurança**  
    > **Manutenibilidade**  
    > **Extensibilidade**

A arquitetura deve ser:

- modular;
- testável;
- legível;
- pequena quando possível;
- desacoplada;
- orientada a contratos;
- segura;
- preparada para evolução.

Evitar:

- overengineering;
- abstrações sem necessidade;
- frameworks desnecessários;
- dependências desnecessárias;
- duplicação;
- código morto;
- funcionalidades "porque talvez sejam úteis".

---

# 4. REGRA MAIS IMPORTANTE

## NÃO REESCREVER O PROJETO DESNECESSARIAMENTE

O projeto já possui uma arquitetura construída progressivamente.

Um agente que assumir o projeto **NÃO** deve:

- apagar módulos existentes;
- substituir Flask sem necessidade;
- substituir a arquitetura de providers;
- trocar o sistema de configuração;
- remover testes;
- recriar a estrutura inteira;
- introduzir outro framework;
- criar uma arquitetura completamente nova.

Antes de qualquer grande mudança:

1. entender o código;
2. identificar o problema;
3. propor a solução;
4. implementar a menor mudança adequada;
5. executar os testes;
6. documentar a decisão.

---

# 5. STACK ATUAL

| Camada | Tecnologia |
|--------|------------|
| **Linguagem** | Python 3.14.6 |
| **Framework** | Flask 3.1.3 |
| **IA** | Provider atualmente utilizado: Kimi / Moonshot AI |
| **HTTP** | requests |
| **Configuração** | python-dotenv |
| **Testes** | pytest 9.1.1 |

---

# 6. AMBIENTE OFICIAL

O ambiente virtual oficial do projeto é:

```
.venv
```

No Windows:

```
.venv\Scripts\python.exe
```

Os testes devem ser executados preferencialmente através dele:

```
.venv\Scripts\python.exe -m pytest tests/ -v
```

Não utilizar o Python global para concluir que o projeto está quebrado quando o `.venv` estiver disponível.

---

# 7. ESTRUTURA ATUAL

A estrutura deve ser verificada no repositório antes de qualquer alteração.

Estrutura conhecida:

```
AquaBot/
│
├── backend/
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── factory.py
│   │   ├── kimi.py
│   │   ├── kimi_client.py
│   │   └── kimi_errors.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   └── logging.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   └── health.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py
│   │   └── app_service.py
│   │
│   ├── __init__.py
│   ├── app.py
│   └── config.py
│
├── database/
│
├── frontend/
│
├── knowledge/
│
├── tests/
│
├── docs/
│
├── .env
├── .env.example
├── .gitignore
├── ARCHITECTURE.md
├── PROJECT_RULES.md
├── README.md
├── requirements.txt
└── AQUABOT_MASTER.md
```

A estrutura acima é uma **referência**.  
O agente deve verificar o estado real do repositório antes de assumir que todos os arquivos continuam exatamente iguais.

---

# 8. ARQUITETURA DE IA

A arquitetura atual de IA é:

```
AIProvider
    │
    ├── KimiProvider
    │       │
    │       ▼
    │   KimiClient
    │
    ▼
AIService
```

Com a introdução da Factory:

```
Configuração
     │
     ▼
ProviderFactory
     │
     ▼
AIProvider
     │
     ▼
KimiProvider
     │
     ▼
KimiClient
```

---

# 9. AIProvider

`AIProvider` é o contrato abstrato para provedores de inteligência artificial.

O restante da aplicação não deve depender diretamente de um provider concreto.

O objetivo é permitir:

```
AIService
    ↓
AIProvider
```

e não:

```
AIService
    ↓
KimiProvider
```

O contrato deve permanecer simples.  
Não adicionar métodos apenas porque futuros providers talvez precisem deles.

---

# 10. KimiProvider

`KimiProvider` é a implementação atual do contrato `AIProvider`.

**Responsabilidades:**
- receber configuração;
- validar API key;
- utilizar `KimiClient`;
- enviar solicitações ao provider;
- converter erros quando necessário;
- fornecer metadata não sensível.

**Não deve:**
- expor API keys;
- armazenar secrets em código;
- misturar responsabilidades de HTTP;
- controlar a aplicação inteira.

---

# 11. KimiClient

`KimiClient` é responsável pela comunicação HTTP com a API do Kimi.

**Responsabilidades:**
- chamadas HTTP;
- autenticação através de variável de ambiente;
- tratamento de timeout;
- tratamento de erro HTTP;
- validação da resposta;
- conversão de erros para `KimiError`.

O restante da aplicação não deve realizar chamadas HTTP diretamente ao Kimi.

---

# 12. AIService

`AIService` representa a camada de serviço utilizada pela aplicação para trabalhar com IA.

Deve depender da abstração:

```
AIProvider
```

e não de:

```
KimiClient
```

ou de APIs específicas.

Exemplo conceitual:

```
Aplicação
    ↓
AIService
    ↓
AIProvider
    ↓
Provider concreto
```

---

# 13. ProviderFactory

A `ProviderFactory` existe para selecionar e instanciar o provider configurado.

Configuração esperada:

```
AI_PROVIDER=kimi
```

Conceito:

```
AI_PROVIDER
     │
     ▼
ProviderFactory
     │
     ▼
KimiProvider
```

**Regras:**
- provider desconhecido deve gerar erro claro;
- seleção deve ser centralizada;
- não espalhar if/elif por toda a aplicação;
- não criar dependência desnecessária de frameworks;
- providers futuros devem poder ser adicionados sem reescrever o restante da aplicação.

---

# 14. METADATA

Providers podem fornecer metadata.

Exemplo:

```json
{
    "provider": "KimiProvider",
    "model": "modelo",
    "api_configured": true
}
```

**Nunca retornar:**
- API key
- token
- secret
- senha
- credencial

`api_configured` deve representar apenas se a configuração necessária está presente.

---

# 15. CONFIGURAÇÃO

A configuração deve permanecer centralizada.

Variáveis sensíveis devem vir do ambiente.

Exemplo:

```
AI_PROVIDER=kimi
KIMI_API_KEY=...
KIMI_MODEL=...
```

O arquivo:

```
.env
```

**NUNCA** deve ser commitado.

O arquivo:

```
.env.example
```

deve documentar as variáveis necessárias sem conter secrets reais.

---

# 16. SEGURANÇA

É proibido colocar no código:

- API keys;
- tokens;
- senhas;
- secrets;
- credenciais;
- chaves privadas.

Também é proibido registrar secrets em logs.

**Nunca imprimir:**

```
KIMI_API_KEY
Authorization
Bearer token
senha
secret
```

em logs.

---

# 17. LOGGING

O sistema possui uma camada de logging em:

```
backend/core/logging.py
```

O logger deve ser reutilizado.

Exemplo conceitual:

```python
from backend.core.logging import get_logger

logger = get_logger("AquaBot")
```

**Níveis principais:**
- INFO
- WARNING
- ERROR

Não criar um sistema de observabilidade complexo sem necessidade.

---

# 18. HEALTH CHECK

O health check existente deve ser preservado.

Endpoint atual:

```
GET /health
```

Não remover ou quebrar esse contrato sem uma decisão arquitetural explícita.

---

# 19. TESTES

Os testes são parte da arquitetura.

Não remover testes para fazer a suíte passar.  
Não diminuir cobertura artificialmente.

Ao adicionar uma funcionalidade:

```
Código
+
Teste
```

devem ser considerados parte da mesma implementação.

**Comando oficial:**

```
.venv\Scripts\python.exe -m pytest tests/ -v
```

---

# 20. ESTADO CONHECIDO DOS TESTES

A **FASE 1.0** terminou com:

- 19 testes
- 19 passed
- 0 failed
- 100%

A **FASE 2.0** foi posteriormente executada e apresentou:

- 34 testes
- 34 passed
- 0 failed
- 100%

O agente deve **confirmar** esses números no estado atual do repositório.  
Não assumir que os números continuam válidos sem executar os testes.

---

# 21. FASES DO PROJETO

## FASE 0 — Auditoria

**Status:** `CONCLUÍDA`

**Objetivo:**
- analisar estrutura;
- analisar arquitetura;
- identificar riscos;
- estabelecer roadmap.

---

## 22. FASE 1.0 — ESTABILIZAÇÃO DA FUNDAÇÃO

**Status:** `CONCLUÍDA`

**Objetivos:**
- dependências;
- configuração;
- logging;
- health check;
- testes;
- documentação.

**Resultado:**
- 19/19 testes
- 100%

---

## 23. FASE 2.0 — INFRAESTRUTURA DE AI PROVIDERS

**Status:** `CONCLUÍDA`

**Objetivos:**
- ProviderFactory;
- seleção por configuração;
- metadata;
- integração Factory + AIService;
- testes.

**Resultado:**
- 34/34 testes
- 100%

**Validação realizada:**
- Git;
- reprodutibilidade;
- arquitetura da Factory;
- segurança;
- documentação;
- testes em ambiente adequado.

---

## 24. FASE 3.0 — CHAT CORE

**Status:** `PLANEJADA`

**NÃO** implementar sem autorização.

**Objetivo futuro:**
Criar o núcleo conversacional do AquaBot.

**Arquitetura prevista:**

```
/api/chat
     │
     ▼
ChatService
     │
     ▼
Mensagem
     │
     ▼
Contexto
     │
     ▼
AIService
     │
     ▼
ProviderFactory
     │
     ▼
KimiProvider
```

**Possíveis componentes:**

```
backend/chat/
backend/services/chat_service.py
backend/models/message.py
```

Os nomes definitivos devem ser definidos somente após análise do código existente.

---

## 25. FASE 4.0 — PERSISTÊNCIA

**Status:** `PLANEJADA`

**Objetivo:**
Adicionar persistência de:
- usuários;
- sessões;
- conversas;
- mensagens;
- configurações;
- histórico.

Não implementar banco de dados antes da definição do modelo de domínio.

---

## 26. FASE 5.0 — AQUABOT ORCHESTRATOR

**Status:** `PLANEJADA`

**Objetivo:**
Criar a camada responsável por coordenar:
- IA
- Memória
- Conhecimento
- Ferramentas
- Contexto
- Regras

O Orchestrator não deve ser criado como um "mega serviço".  
Responsabilidades devem permanecer separadas.

---

## 27. FASE 6.0 — KNOWLEDGE / RAG

**Status:** `PLANEJADA`

**Objetivo futuro:**
Permitir ao AquaBot trabalhar com conhecimento próprio.

**Possíveis fontes:**
- documentos;
- materiais didáticos;
- informações da Aquarius;
- conteúdos autorizados;
- documentação técnica.

A arquitetura definitiva deverá ser decidida quando essa fase começar.  
Não introduzir vector database prematuramente.

---

## 28. FASE 7.0 — FRONTEND

**Status:** `PLANEJADA`

**Objetivo:**
Criar a interface web do AquaBot.

O frontend deverá consumir APIs do backend.  
Não misturar regras de negócio complexas dentro da interface.

---

# 29. FUNCIONALIDADES FUTURAS

As seguintes funcionalidades podem ser consideradas futuramente:

- memória;
- RAG;
- knowledge base;
- ferramentas;
- autenticação;
- autorização;
- rate limiting;
- streaming;
- múltiplos providers;
- voz;
- painel administrativo;
- analytics;
- observabilidade;
- integração com serviços externos.

Nenhuma deve ser implementada antecipadamente sem estar associada a uma fase autorizada.

---

# 30. MULTIPLE PROVIDERS

O projeto está preparado conceitualmente para múltiplos providers.

Entretanto:

**Não** implementar OpenAI, Gemini, Claude ou outros providers apenas por antecipação.

Primeiro consolidar:

```
AIProvider
ProviderFactory
KimiProvider
AIService
Chat Core
```

Depois avaliar se múltiplos providers são realmente necessários.

---

# 31. FRONTEND

O frontend ainda não deve ser tratado como prioridade durante a construção do núcleo.

A prioridade é:

```
Backend
    ↓
Contratos
    ↓
Chat Core
    ↓
Persistência
    ↓
Orchestrator
    ↓
Knowledge
    ↓
Frontend
```

---

# 32. BANCO DE DADOS

O diretório:

```
database/
```

pode existir antes da implementação da persistência.  
Isso não significa que o banco já esteja implementado.

Não criar tabelas arbitrárias.

Antes de implementar persistência:

1. definir entidades;
2. definir relacionamentos;
3. definir regras;
4. definir migrações;
5. criar testes;
6. somente então implementar.

---

# 33. DOCUMENTAÇÃO

**Documentação principal:**
- `AQUABOT_MASTER.md`
- `PROJECT_RULES.md`
- `ARCHITECTURE.md`
- `README.md`

**Documentação complementar:**
- `docs/architecture.md`
- `docs/development.md`
- `docs/api.md`

Não criar documentação duplicada sem necessidade.

Quando houver conflito:

1. código/testes representam o estado real;
2. `PROJECT_RULES.md` representa regras de desenvolvimento;
3. `AQUABOT_MASTER.md` representa direção e continuidade;
4. documentação específica representa detalhes da respectiva área.

Divergências devem ser identificadas e corrigidas conscientemente.

---

# 34. GIT

Antes de alterações:

```
git status
```

Depois:

```
git diff
git status
```

Antes de concluir uma fase:

```
git log --oneline -10
```

Commits devem ser pequenos e semanticamente claros.

Exemplos:

```
feat: adicionar ProviderFactory
test: adicionar testes da ProviderFactory
docs: atualizar arquitetura de providers
fix: corrigir tratamento de erro do provider
```

Não realizar:

```
git reset --hard
git clean -fd
```

sem autorização explícita.

---

# 35. ALTERAÇÕES DE ARQUIVOS

Antes de editar:

1. ler o arquivo;
2. entender dependências;
3. verificar testes;
4. verificar documentação;
5. alterar somente o necessário.

Não substituir arquivos inteiros quando uma alteração pequena resolver o problema.

---

# 36. NOVAS DEPENDÊNCIAS

Não adicionar dependências simplesmente por conveniência.

Antes de adicionar uma biblioteca:

1. verificar se a funcionalidade pode ser implementada com a biblioteca padrão;
2. verificar se já existe dependência equivalente;
3. avaliar manutenção;
4. avaliar segurança;
5. avaliar compatibilidade com Python 3.14;
6. adicionar versão apropriada;
7. atualizar documentação quando necessário;
8. adicionar testes.

---

# 37. TEST-DRIVEN DEVELOPMENT

Para funcionalidades importantes:

```
Requisito
   ↓
Teste
   ↓
Implementação
   ↓
Refatoração
   ↓
Testes
```

Nunca considerar:

> "funciona manualmente"

como substituto de testes automatizados.

---

# 38. TRATAMENTO DE ERROS

Erros devem:
- ser claros;
- ser previsíveis;
- ser testáveis;
- não expor secrets;
- manter contexto suficiente para diagnóstico.

Não retornar stack traces internos ao usuário final em produção.

---

# 39. API

A API futura deverá possuir contratos claros.

Exemplo futuro:

```
POST /api/chat
```

**Entrada prevista conceitualmente:**

```json
{
  "message": "Olá, AquaBot"
}
```

**Resposta futura:**

```json
{
  "response": "Olá! Como posso ajudar?"
}
```

Isso é apenas uma referência conceitual.  
O contrato definitivo deverá ser definido durante a **FASE 3.0**.

---

# 40. CONTEXTO E MEMÓRIA

O AquaBot futuramente deverá diferenciar:

- **Mensagem atual**
- **Contexto da conversa**
- **Memória persistente**
- **Conhecimento externo**

Não misturar esses conceitos.

Exemplo:

```
Mensagem
    ↓
Contexto imediato

Memória
    ↓
Informações persistentes

Knowledge
    ↓
Informações externas/documentais
```

---

# 41. RAG

RAG não deve ser implementado simplesmente como:

```
PDF → embeddings → banco vetorial
```

Antes disso devem existir:
- ingestão;
- processamento;
- chunking;
- metadata;
- indexação;
- recuperação;
- ranking;
- contexto;
- avaliação.

A arquitetura deverá ser definida na FASE 6.

---

# 42. ORQUESTRADOR

O Orchestrator deverá futuramente coordenar componentes.

**Não** deverá:
- conter todo o código do sistema;
- conhecer detalhes de banco;
- conhecer diretamente APIs externas;
- misturar HTTP com regras de negócio;
- substituir todos os services.

---

# 43. AGENTES DE DESENVOLVIMENTO

Qualquer agente que assumir o projeto deverá seguir este procedimento:

1. Ler `AQUABOT_MASTER.md`
2. Ler `PROJECT_RULES.md`
3. Ler `ARCHITECTURE.md`
4. Verificar `git status`
5. Inspecionar código relevante
6. Executar testes
7. Diagnosticar
8. Propor alteração
9. Implementar somente após autorização quando a tarefa exigir
10. Executar testes
11. Revisar diff
12. Atualizar documentação
13. Relatar resultado

---

# 44. MODO DE TRABALHO DOS AGENTES

Quando o usuário solicitar:

> "analise"

Não modificar código.

Quando o usuário solicitar:

> "implemente"

Modificar somente o escopo autorizado.

Quando o usuário solicitar:

> "continue"

Primeiro verificar o estado real do projeto.

Nunca assumir que uma fase está concluída apenas porque este documento diz que deveria estar.

---

# 45. REGRA CONTRA AVANÇO AUTOMÁTICO

Concluir uma fase **NÃO** autoriza automaticamente a próxima.

Exemplo:

```
FASE 2 concluída
```

não significa:

```
implementar FASE 3
```

O agente deve:

1. executar os critérios de aceite;
2. apresentar relatório;
3. aguardar autorização.

---

# 46. CRITÉRIOS GERAIS DE CONCLUSÃO

Uma fase somente pode ser considerada concluída quando:

- implementação realizada;
- testes adicionados;
- testes existentes passando;
- documentação atualizada;
- Git revisado;
- segurança revisada;
- critérios de aceite cumpridos;
- nenhuma alteração inesperada presente.

---

# 47. RELATÓRIO PADRÃO

Ao finalizar uma tarefa importante, apresentar:

**Status**
- CONCLUÍDO
- ou NÃO CONCLUÍDO

**Alterações**
- Lista dos arquivos modificados.

**Arquivos criados**
- Lista.

**Arquivos removidos**
- Lista.

**Testes**
- Total:
- Passaram:
- Falharam:

**Segurança**
- Informar se houve impacto.

**Documentação**
- Informar arquivos atualizados.

**Dívidas técnicas**
- Informar problemas restantes.

**Próximo passo**
- Somente recomendar.
- Não executar automaticamente.

---

# 48. CHECKLIST DE SEGURANÇA

Antes de concluir uma fase:

- [ ] nenhum secret hardcoded;
- [ ] `.env` não está versionado;
- [ ] `.env.example` não possui credenciais reais;
- [ ] logs não expõem secrets;
- [ ] erros não expõem credenciais;
- [ ] APIs externas utilizam configuração segura;
- [ ] entradas futuras serão validadas;
- [ ] dependências foram revisadas.

---

# 49. CHECKLIST DE QUALIDADE

Antes de concluir:

- [ ] código legível;
- [ ] responsabilidades separadas;
- [ ] testes atualizados;
- [ ] sem código morto;
- [ ] sem imports desnecessários;
- [ ] sem dependências desnecessárias;
- [ ] sem duplicação evidente;
- [ ] documentação consistente;
- [ ] Git revisado.

---

# 50. ROADMAP RESUMIDO

```
┌────────────────────────────────────┐
│ AUDITORIA                          │
│ ✅ CONCLUÍDA                       │
└─────────────────┬──────────────────┘
                  │
                  ▼
┌────────────────────────────────────┐
│ FASE 1.0                           │
│ FUNDAÇÃO                           │
│ ✅ CONCLUÍDA                       │
│ 19/19 testes                       │
└─────────────────┬──────────────────┘
                  │
                  ▼
┌────────────────────────────────────┐
│ FASE 2.0                           │
│ AI PROVIDERS                       │
│ ✅ IMPLEMENTADA / VALIDAR          │
│ 34/34 testes                       │
└─────────────────┬──────────────────┘
                  │
                  ▼
┌────────────────────────────────────┐
│ FASE 3.0                           │
│ CHAT CORE                           │
│ ⏳ PLANEJADA                        │
└─────────────────┬──────────────────┘
                  │
                  ▼
┌────────────────────────────────────┐
│ FASE 4.0                           │
│ PERSISTÊNCIA                        │
│ ⏳ PLANEJADA                        │
└─────────────────┬──────────────────┘
                  │
                  ▼
┌────────────────────────────────────┐
│ FASE 5.0                           │
│ ORQUESTRADOR                        │
│ ⏳ PLANEJADA                        │
└─────────────────┬──────────────────┘
                  │
                  ▼
┌────────────────────────────────────┐
│ FASE 6.0                           │
│ KNOWLEDGE / RAG                    │
│ ⏳ PLANEJADA                        │
└─────────────────┬──────────────────┘
                  │
                  ▼
┌────────────────────────────────────┐
│ FASE 7.0                           │
│ FRONTEND                            │
│ ⏳ PLANEJADA                        │
└────────────────────────────────────┘
```

---

# 51. ESTADO ATUAL DE REFERÊNCIA

No momento da criação deste documento:

| Item | Valor |
|------|-------|
| **Projeto** | AquaBot |
| **Python** | 3.14.6 |
| **Framework** | Flask |
| **Provider** | Kimi |
| **Ambiente** | .venv |
| **FASE 1.0** | CONCLUÍDA |
| **FASE 2.0** | IMPLEMENTADA / EM VALIDAÇÃO |
| **Testes informados** | 34 passed |
| **Próxima fase** | FASE 3.0 — CHAT CORE |

Antes de avançar, o agente deve confirmar o estado real.

---

# 52. VISÃO DE LONGO PRAZO

O objetivo final não é apenas criar um chatbot.

O objetivo é construir uma plataforma AquaBot capaz de:

```
CONVERSAR
    +
COMPREENDER CONTEXTO
    +
LEMBRAR
    +
CONSULTAR CONHECIMENTO
    +
UTILIZAR FERRAMENTAS
    +
EXECUTAR FLUXOS
    +
INTEGRAR SERVIÇOS
```

Sempre mantendo:

```
controle
segurança
testabilidade
modularidade
```

---

# 53. REGRA FINAL PARA QUALQUER AGENTE

Antes de alterar qualquer coisa, pergunte:

> Qual problema concreto esta alteração resolve?

Depois:

> Existe uma solução mais simples?

Depois:

> Como isso será testado?

Depois:

> Isso quebra alguma arquitetura existente?

Depois:

> Isso pertence à fase atual?

Se a resposta não estiver clara:

**NÃO IMPLEMENTAR.**  
Analisar primeiro.

---

# 54. AUTORIDADE FINAL

Este documento é um guia de continuidade.

Ele não substitui a análise do código real.

O estado real do repositório sempre deve ser verificado.

Em caso de divergência entre documentação e código:

```
Código + testes
```

devem ser usados para identificar o estado atual.

A divergência deve ser documentada e corrigida conscientemente.

---

# FIM DO AQUABOT MASTER

Este arquivo deve permanecer na raiz do repositório:

```
AquaBot/AQUABOT_MASTER.md
```

Todo novo agente deve lê-lo antes de iniciar o desenvolvimento.
