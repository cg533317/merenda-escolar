"""
AquaBot — Política de Contexto
==============================

Responsabilidade:
    Definir como o histórico de mensagens é transformado em contexto
    a ser enviado ao provedor de IA.

Esta camada é uma abstração para permitir a evolução futura para
políticas mais sofisticadas (ex: gerenciamento de tokens, resumo,
seleção semântica) sem alterar a cadeia de IA.

Responsabilidades:
    - decidir quais mensagens do histórico compõem o contexto;
    - transformar mensagens persistentes em linhas de contexto.

Não é responsabilidade desta camada:
    - persistência;
    - comunicação com provedores de IA;
    - regras de negócio do chat.
"""

from __future__ import annotations

from typing import Any, Protocol


class ContextPolicy(Protocol):
    """Contrato de políticas de contexto conversacional."""

    def build_context(self, messages: list[Any]) -> str:
        """Transforma o histórico de mensagens em contexto textual."""
        ...


class MostRecentContextPolicy:
    """
    Política que utiliza as mensagens mais recentes do histórico.

    O limite de mensagens é configurável via `max_messages`, permitindo
    ajuste sem alterar a política ou a cadeia de IA.
    """

    def __init__(self, max_messages: int = 10):
        if max_messages < 1:
            raise ValueError("max_messages deve ser maior ou igual a 1.")

        self.max_messages = max_messages

    def build_context(self, messages: list[Any]) -> str:
        """Retorna as mensagens mais recentes formatadas como contexto."""
        recent = messages[-self.max_messages:]

        lines = []
        for message in recent:
            role = message.role
            content = message.content
            lines.append(f"{role}: {content}")

        return "\n".join(lines)
