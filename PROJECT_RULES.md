# AQUABOT - REGRAS DO PROJETO

## 1. REGRA PRINCIPAL

Este projeto deve ser tratado como um sistema real em desenvolvimento.

Nenhuma IA pode modificar, apagar, renomear ou mover arquivos fora do escopo explícito da tarefa.

---

## 2. ANTES DE ALTERAR

Antes de modificar qualquer arquivo:

1. Ler o arquivo completo quando necessário.
2. Identificar suas dependências.
3. Verificar quem utiliza suas funções, classes ou componentes.
4. Entender o comportamento atual.
5. Definir exatamente o que será alterado.

---

## 3. PROIBIDO SEM AUTORIZAÇÃO

Uma IA NÃO deve:

- apagar funcionalidades existentes;
- reescrever arquivos inteiros sem necessidade;
- alterar arquitetura por iniciativa própria;
- trocar bibliotecas sem autorização;
- mudar banco de dados sem autorização;
- alterar APIs sem autorização;
- alterar layout por iniciativa própria;
- renomear pastas ou arquivos sem autorização;
- remover código aparentemente desnecessário sem comprovar que não é utilizado;
- modificar arquivos fora do escopo da tarefa.

---

## 4. ALTERAÇÕES MÍNIMAS

Sempre preferir a menor alteração possível para resolver o problema.

Não transformar uma correção pequena em uma refatoração completa.

---

## 5. TESTES

Depois de qualquer alteração:

1. Executar os testes relacionados.
2. Verificar erros.
3. Verificar se funcionalidades existentes continuam funcionando.
4. Informar claramente o resultado.

---

## 6. PROBLEMAS FORA DO ESCOPO

Se a IA encontrar outro problema enquanto trabalha:

NÃO corrigir automaticamente.

Deve informar:

- arquivo;
- problema encontrado;
- possível impacto;
- sugestão de correção.

A correção somente ocorrerá mediante autorização.

---

## 7. SEGURANÇA

Nunca colocar:

- senhas;
- tokens;
- API keys;
- credenciais;
- chaves privadas;

diretamente no código.

Utilizar variáveis de ambiente.

---

## 8. BANCO DE DADOS

Alterações estruturais no banco devem ser tratadas como mudanças críticas.

Nunca apagar ou recriar dados sem autorização explícita.

---

## 9. INTELIGÊNCIA ARTIFICIAL

O AquaBot poderá utilizar múltiplas IAs.

Cada IA deve trabalhar como um agente especializado.

Uma IA não deve assumir que pode modificar o trabalho realizado por outra IA sem verificar o estado atual do projeto.

---

## 10. REVISÃO

Sempre que possível:

IA 1 -> implementação

IA 2 -> revisão

Testes -> validação

Humano -> decisão final

---

## 11. PRINCÍPIO FUNDAMENTAL

FUNCIONANDO > REESCREVER

ESTÁVEL > MAIS COMPLEXO

PEQUENA ALTERAÇÃO > GRANDE REFACTOR

TESTAR > SUPOR

ANALISAR > MODIFICAR

---

## 12. AUTORIZAÇÃO

A palavra "corrigir" não significa autorização para modificar todo o projeto.

A alteração deve permanecer limitada ao problema solicitado.

---

## 13. DOCUMENTAÇÃO

Alterações arquiteturais importantes devem ser documentadas.

---

## 14. REGRA PARA O KIMI

O Kimi deve respeitar integralmente este arquivo.

Antes de executar mudanças significativas, deve informar:

- o que pretende alterar;
- quais arquivos serão afetados;
- por que serão alterados;
- quais riscos existem.

---

## 15. REGRA PARA OUTRAS IAs

Qualquer outra IA que trabalhar no AquaBot deverá ler este arquivo antes de realizar alterações.

---

## VERSÃO

Projeto: AquaBot
Documento: PROJECT_RULES
Versão: 1.0
Status: Fundação inicial

---

## 16. COLABORAÇÃO ENTRE IAs

Quando duas ou mais IAs trabalharem no projeto:

1. Cada IA deve ler o estado atual do projeto antes de trabalhar.
2. Nenhuma IA deve sobrescrever alterações de outra IA sem verificar o motivo e o estado atual dos arquivos.
3. A IA responsável pela revisão não deve modificar o código automaticamente apenas por encontrar um possível problema.
4. A revisão deve primeiro apresentar:
   - problema encontrado;
   - arquivo afetado;
   - evidência;
   - impacto;
   - correção sugerida.
5. Alterações identificadas pela revisão somente serão implementadas após autorização ou quando estiverem explicitamente dentro do escopo da tarefa.
6. Uma IA nunca deve desfazer uma alteração apenas porque foi criada por outra IA.
7. Em caso de conflito entre decisões técnicas, a decisão final pertence ao responsável pelo projeto.
8. O histórico das alterações deve ser preservado sempre que possível através de Git.
9. Antes de uma alteração significativa, deve ser possível identificar:
   - estado anterior;
   - alteração realizada;
   - motivo da alteração;
   - resultado dos testes.

### Fluxo recomendado

ANÁLISE
   ↓
PLANEJAMENTO
   ↓
IA IMPLEMENTADORA
   ↓
REVISÃO INDEPENDENTE
   ↓
TESTES
   ↓
APROVAÇÃO HUMANA
   ↓
PRÓXIMA ALTERAÇÃO

---

## 17. GIT COMO PONTO DE SEGURANÇA

O Git deve ser utilizado para preservar o histórico do projeto.

Antes de alterações significativas, sempre que possível:

1. verificar o estado atual do repositório;
2. registrar alterações existentes;
3. realizar a mudança;
4. executar testes;
5. verificar o resultado;
6. registrar a alteração quando apropriado.

Nenhuma IA deve apagar ou sobrescrever histórico do projeto sem autorização explícita.

