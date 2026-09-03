"""
AquaBot — Identificação de Usuário
==================================

Responsabilidade:
    Fornecer a identidade do usuário atual para as operações de chat.

Nesta fase ainda não existe autenticação completa. Por isso a identidade
é resolvida por um provedor injetado, permitindo substituição futura por
autenticação real sem reconstruir a arquitetura conversacional.

A identidade técnica NÃO é hardcoded no ChatService: ela é fornecida por
uma instância de `IdentityProvider` injetada no serviço.
"""

from __future__ import annotations

from typing import Protocol

from backend.config import Config


class IdentityProvider(Protocol):
    """Contrato para resolver a identidade do usuário atual."""

    def get_username(self) -> str:
        """Retorna o identificador estável do usuário atual."""
        ...

    def get_display_name(self) -> str | None:
        """Retorna o nome de exibição do usuário atual (opcional)."""
        ...


class TechnicalIdentityProvider:
    """
    Identidade técnica controlada para o ambiente atual.

    Em fases futuras, a autenticação real substituirá esta implementação
    sem necessidade de alterar o ChatService.
    """

    def __init__(self, username: str | None = None, display_name: str | None = None):
        self._username = username or Config.TECHNICAL_USERNAME
        self._display_name = (
            display_name if display_name is not None else Config.TECHNICAL_DISPLAY_NAME
        )

    def get_username(self) -> str:
        return self._username

    def get_display_name(self) -> str | None:
        return self._display_name
