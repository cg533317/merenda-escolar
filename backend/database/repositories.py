"""
AquaBot — Repositories
======================

Camada responsável exclusivamente pela persistência das entidades.

Responsabilidades:
    - consultar entidades;
    - criar entidades;
    - atualizar estado persistente;
    - controlar operações de leitura e escrita.

Não é responsabilidade dos Repositories:
    - regras de negócio;
    - HTTP;
    - Flask;
    - IA;
    - autenticação;
    - gerenciamento de secrets;
    - commit automático de transações.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.database.models import (
    Conversation,
    Message,
    Session as SessionModel,
    User,
)


class UserRepository:
    """Repository para operações de persistência de User."""

    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        username: str,
        display_name: str | None = None,
        status: str = "active",
    ) -> User:
        user = User(
            id=uuid4(),
            username=username,
            display_name=display_name,
            status=status,
        )

        self.session.add(user)

        return user

    def get_by_id(self, user_id: UUID) -> User | None:
        return self.session.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        statement = select(User).where(User.username == username)

        return self.session.scalar(statement)

    def update(
        self,
        user: User,
        *,
        username: str | None = None,
        display_name: str | None = None,
        status: str | None = None,
    ) -> User:
        if username is not None:
            user.username = username

        if display_name is not None:
            user.display_name = display_name

        if status is not None:
            user.status = status

        user.updated_at = datetime.now(timezone.utc)

        return user


class SessionRepository:
    """Repository para operações de persistência de Session."""

    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        user_id: UUID,
        status: str = "active",
    ) -> SessionModel:
        now = datetime.now(timezone.utc)

        session = SessionModel(
            id=uuid4(),
            user_id=user_id,
            started_at=now,
            last_activity_at=now,
            status=status,
        )

        self.session.add(session)

        return session

    def get_by_id(
        self,
        session_id: UUID,
    ) -> SessionModel | None:
        return self.session.get(SessionModel, session_id)

    def update_activity(
        self,
        session: SessionModel,
    ) -> SessionModel:
        session.last_activity_at = datetime.now(timezone.utc)

        return session

    def end(
        self,
        session: SessionModel,
    ) -> SessionModel:
        session.status = "ended"
        session.ended_at = datetime.now(timezone.utc)

        return session


class ConversationRepository:
    """Repository para operações de persistência de Conversation."""

    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        user_id: UUID,
        title: str | None = None,
        status: str = "active",
    ) -> Conversation:
        conversation = Conversation(
            id=uuid4(),
            user_id=user_id,
            title=title,
            status=status,
        )

        self.session.add(conversation)

        return conversation

    def get_by_id(
        self,
        conversation_id: UUID,
    ) -> Conversation | None:
        return self.session.get(
            Conversation,
            conversation_id,
        )

    def get_by_id_for_user(
        self,
        conversation_id: UUID,
        user_id: UUID,
    ) -> Conversation | None:
        """
        Recupera uma Conversation somente se pertencer ao usuário.

        Simula o conceito de `conversation.user_id == user_id`. A consulta
        é feita pela identidade do usuário, de modo que um usuário não
        consiga acessar conversa de terceiros — o retorno é None tanto
        para conversa inexistente quanto para conversa de outro usuário.
        """
        statement = (
            select(Conversation)
            .where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )

        return self.session.scalar(statement)

    def list_by_user(
        self,
        user_id: UUID,
    ) -> list[Conversation]:
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.asc())
        )

        return list(self.session.scalars(statement))

    def update(
        self,
        conversation: Conversation,
        *,
        title: str | None = None,
        status: str | None = None,
    ) -> Conversation:
        if title is not None:
            conversation.title = title

        if status is not None:
            conversation.status = status

        conversation.updated_at = datetime.now(timezone.utc)

        return conversation

    def update_status(
        self,
        conversation: Conversation,
        status: str,
    ) -> Conversation:
        conversation.status = status
        conversation.updated_at = datetime.now(timezone.utc)

        return conversation


class MessageRepository:
    """Repository para operações de persistência de Message."""

    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        conversation_id: UUID,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> Message:
        last_sequence = self.get_last_sequence(conversation_id)

        message = Message(
            id=uuid4(),
            conversation_id=conversation_id,
            sequence=last_sequence + 1,
            role=role,
            content=content,
            metadata_=metadata,
        )

        self.session.add(message)

        return message

    def get_by_id(
        self,
        message_id: UUID,
    ) -> Message | None:
        return self.session.get(Message, message_id)

    def list_by_conversation(
        self,
        conversation_id: UUID,
    ) -> list[Message]:
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.sequence.asc())
        )

        return list(self.session.scalars(statement))

    def get_last_sequence(
        self,
        conversation_id: UUID,
    ) -> int:
        statement = select(
            func.max(Message.sequence)
        ).where(
            Message.conversation_id == conversation_id
        )

        result = self.session.scalar(statement)

        return result if result is not None else 0
