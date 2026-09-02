"""
AquaBot — Modelos de Persistência
==================================

Modelos SQLAlchemy correspondentes ao domínio persistente do AquaBot.

Entidades:
    User
    Session
    Conversation
    Message

Regras arquiteturais:
    - Models representam dados e relacionamentos.
    - Regras de aplicação pertencem aos Services.
    - Operações de persistência pertencem aos Repositories.
    - Secrets e credenciais não fazem parte do domínio persistente.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid


class Base(DeclarativeBase):
    """Classe base dos modelos persistentes do AquaBot."""


def utc_now() -> datetime:
    """Retorna o instante atual em UTC."""
    return datetime.now(timezone.utc)


class User(Base):
    """Usuário persistente do AquaBot."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    username: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    display_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
    )

    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=utc_now,
    )

    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    sessions: Mapped[list[Session]] = relationship(
        back_populates="user",
    )

    conversations: Mapped[list[Conversation]] = relationship(
        back_populates="user",
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'inactive')",
            name="ck_users_status",
        ),
    )


class Session(Base):
    """Sessão de utilização do AquaBot."""

    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=utc_now,
    )

    last_activity_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=utc_now,
    )

    ended_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
    )

    user: Mapped[User] = relationship(
        back_populates="sessions",
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'ended', 'expired')",
            name="ck_sessions_status",
        ),
        Index("ix_sessions_user_id", "user_id"),
    )


class Conversation(Base):
    """Conversa persistente do AquaBot."""

    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
    )

    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=utc_now,
    )

    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    user: Mapped[User] = relationship(
        back_populates="conversations",
    )

    messages: Mapped[list[Message]] = relationship(
        back_populates="conversation",
        order_by="Message.sequence",
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'ended', 'archived')",
            name="ck_conversations_status",
        ),
        Index("ix_conversations_user_id", "user_id"),
    )


class Message(Base):
    """Mensagem persistente pertencente a uma Conversation."""

    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("conversations.id", ondelete="RESTRICT"),
        nullable=False,
    )

    sequence: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    metadata_: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=utc_now,
    )

    conversation: Mapped[Conversation] = relationship(
        back_populates="messages",
    )

    __table_args__ = (
        UniqueConstraint(
            "conversation_id",
            "sequence",
            name="uq_messages_conversation_sequence",
        ),
        CheckConstraint(
            "role IN ('user', 'assistant')",
            name="ck_messages_role",
        ),
        CheckConstraint(
            "length(trim(content)) > 0",
            name="ck_messages_content_not_blank",
        ),
        Index("ix_messages_conversation_id", "conversation_id"),
    )