# AQUABOT - ARQUITETURA DO PROJETO

## 1. OBJETIVO

O AquaBot é um sistema de inteligência artificial desenvolvido para o projeto Aquarius.

A arquitetura deve permitir evolução gradual, manutenção segura, integração com múltiplos modelos de IA e separação clara entre interface, regras de negócio, inteligência artificial, conhecimento, banco de dados e testes.

---

## 2. PRINCÍPIOS DA ARQUITETURA

A arquitetura deve seguir os seguintes princípios:

- Separação de responsabilidades.
- Baixo acoplamento entre componentes.
- Código organizado e previsível.
- Alterações pequenas e controladas.
- Facilidade de testes.
- Facilidade de manutenção.
- Segurança por padrão.
- Preparação para múltiplas IAs.
- Nenhum componente deve assumir responsabilidades de outro sem necessidade.

---

## 3. ESTRUTURA PRINCIPAL

A estrutura principal do projeto é:

AquaBot/
│
├── backend/
│   ├── ai/
│   ├── routes/
│   └── services/
│
├── database/
│
├── frontend/
│   ├── css/
│   └── js/
│
├── knowledge/
│
├── tests/
│
├── .gitignore
├── README.md
├── PROJECT_RULES.md
└── ARCHITECTURE.md

---

## 4. BACKEND

A pasta backend contém a lógica do servidor e a coordenação das funcionalidades do sistema.

### backend/ai/

Responsável pela integração com modelos e serviços de inteligência artificial.

Responsabilidades possíveis:

- comunicação com provedores de IA;
- gerenciamento de modelos;
- construção e execução de prompts;
- tratamento das respostas das IAs;
- controle de agentes;
- definição das funções de cada agente;
- mecanismos de revisão entre IAs.

Esta camada não deve conter diretamente regras específicas da interface.

---

### backend/routes/

Responsável pelas rotas e endpoints da aplicação.

Responsabilidades:

- receber requisições;
- validar entradas básicas;
- chamar os serviços apropriados;
- devolver respostas ao frontend;
- controlar códigos e formatos de resposta.

As rotas não devem concentrar regras complexas de negócio.

---

### backend/services/

Responsável pelas regras e serviços da aplicação.

Responsabilidades:

- regras de negócio;
- processamento de dados;
- comunicação com banco de dados através das abstrações apropriadas;
- operações utilizadas pelas rotas;
- coordenação entre diferentes componentes.

As regras de negócio devem permanecer preferencialmente nesta camada, e não diretamente nas rotas.

---

## 5. DATABASE

A pasta database será responsável pelos componentes relacionados ao armazenamento persistente de dados.

Responsabilidades possíveis:

- configuração do banco;
- modelos;
- consultas;
- migrações;
- inicialização;
- estruturas relacionadas ao armazenamento.

Alterações estruturais no banco são consideradas mudanças críticas e devem obedecer ao PROJECT_RULES.md.

Nenhuma IA poderá apagar ou recriar dados sem autorização explícita.

---

## 6. FRONTEND

A pasta frontend contém a interface utilizada pelo usuário.

### frontend/css/

Responsável pelos estilos visuais.

### frontend/js/

Responsável pela lógica executada no navegador.

O frontend deve se comunicar com o backend através das interfaces definidas pelas rotas.

A interface não deve conter regras críticas de negócio que deveriam estar protegidas no backend.

---

## 7. KNOWLEDGE

A pasta knowledge representa a base de conhecimento utilizada pelo AquaBot.

Pode conter futuramente:

- documentos;
- informações estruturadas;
- conteúdos de referência;
- instruções;
- dados utilizados pelos agentes;
- índices ou estruturas auxiliares de conhecimento.

Conteúdo de conhecimento deve ser separado do código da aplicação sempre que possível.

---

## 8. TESTS

A pasta tests contém os testes automatizados do projeto.

Os testes devem verificar, conforme a evolução do sistema:

- serviços;
- rotas;
- integração;
- componentes de IA;
- acesso ao banco;
- regras de negócio;
- funcionalidades críticas.

Toda funcionalidade importante deve possuir testes apropriados antes de ser considerada estável.

---

## 9. MULTIPLAS IAs

O AquaBot será projetado para permitir a utilização de múltiplas IAs.

Cada IA deverá possuir uma responsabilidade claramente definida.

Arquitetura conceitual:

IA IMPLEMENTADORA
        │
        ▼
ALTERAÇÃO CONTROLADA
        │
        ▼
IA REVISORA
        │
        ▼
ANÁLISE
        │
        ▼
TESTES
        │
        ▼
DECISÃO HUMANA

Nenhuma IA deve assumir autoridade sobre o projeto inteiro.

---

## 10. SEPARAÇÃO ENTRE IMPLEMENTAÇÃO E REVISÃO

A IA responsável pela implementação deve concentrar-se na tarefa solicitada.

A IA responsável pela revisão deve analisar:

- qualidade;
- segurança;
- possíveis erros;
- regressões;
- compatibilidade;
- aderência à arquitetura;
- aderência ao PROJECT_RULES.md.

A IA revisora deve apresentar problemas encontrados antes de realizar alterações fora do escopo.

---

## 11. FLUXO DE DADOS

O fluxo conceitual principal será:

USUÁRIO
   │
   ▼
FRONTEND
   │
   ▼
BACKEND / ROUTES
   │
   ▼
SERVICES
   │
   ├──────────────► DATABASE
   │
   ├──────────────► KNOWLEDGE
   │
   ▼
AI
   │
   ▼
MODELO DE IA
   │
   ▼
AI / SERVICES
   │
   ▼
BACKEND
   │
   ▼
FRONTEND
   │
   ▼
USUÁRIO

A implementação concreta desse fluxo poderá evoluir sem quebrar os princípios de separação de responsabilidades.

---

## 12. SEGURANÇA

Credenciais, tokens, API keys e informações sensíveis não devem ser armazenados diretamente no código.

As configurações sensíveis deverão utilizar variáveis de ambiente ou mecanismos seguros equivalentes.

O frontend nunca deve receber segredos destinados exclusivamente ao backend.

---

## 13. CONFIGURAÇÃO

Configurações do sistema devem ser centralizadas quando necessário.

Evitar valores críticos espalhados por diversos arquivos.

A configuração deve permitir diferentes ambientes futuramente, como:

- desenvolvimento;
- testes;
- produção.

---

## 14. DEPENDÊNCIAS

Novas bibliotecas somente devem ser adicionadas quando houver necessidade real.

Antes de adicionar uma dependência, deve-se avaliar:

- necessidade;
- compatibilidade;
- segurança;
- manutenção;
- impacto no projeto;
- alternativas existentes.

Nenhuma IA deve adicionar bibliotecas simplesmente para resolver problemas que podem ser resolvidos adequadamente com os componentes existentes.

---

## 15. EVOLUÇÃO DA ARQUITETURA

A arquitetura inicial não deve ser considerada definitiva.

Alterações arquiteturais poderão ocorrer quando houver necessidade comprovada.

Mudanças significativas devem:

1. ser justificadas;
2. indicar os arquivos afetados;
3. avaliar impactos;
4. ser documentadas;
5. respeitar o PROJECT_RULES.md;
6. ser testadas.

---

## 16. REGRA DE COMPATIBILIDADE

Novos componentes devem evitar quebrar funcionalidades existentes.

Sempre que possível, mudanças devem ser retrocompatíveis.

Quando uma mudança incompatível for necessária, ela deverá ser explicitamente identificada e autorizada.

---

## 17. DOCUMENTOS DE AUTORIDADE

Os documentos fundamentais do projeto são:

PROJECT_RULES.md
    Define as regras de trabalho das IAs.

ARCHITECTURE.md
    Define os princípios e a organização técnica do sistema.

README.md
    Apresenta o projeto e sua finalidade.

Em caso de conflito:

1. Segurança e integridade do projeto.
2. PROJECT_RULES.md.
3. ARCHITECTURE.md.
4. Escopo explícito da tarefa.
5. Decisão do responsável pelo projeto.

---

## 18. ESTADO DA ARQUITETURA

Status: Fundação inicial.

A estrutura atual representa a arquitetura inicial do AquaBot.

Nenhuma implementação complexa deve ser iniciada antes da definição dos componentes necessários.

---

## VERSÃO

Projeto: AquaBot
Documento: ARCHITECTURE
Versão: 1.0
Status: Fundação inicial
