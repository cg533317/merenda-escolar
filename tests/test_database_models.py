"""
Testes de contrato dos Models de persistência do AquaBot.

Estes testes protegem as decisões estruturais aprovadas na FASE 4.1.
"""

import uuid

from sqlalchemy import CheckConstraint, UniqueConstraint

from backend.database.models import (
    Base,
    Conversation,
    Message,
    Session,
    User,
)


def test_models_are_registered():
    """Todas as entidades persistentes devem estar registradas no metadata."""
    assert set(Base.metadata.tables) == {
        "users",
        "sessions",
        "conversations",
        "messages",
    }


def test_all_models_have_uuid_primary_key():
    """Todas as entidades devem possuir UUID como identidade primária."""
    for model in (User, Session, Conversation, Message):
        primary_key = model.__table__.primary_key

        assert len(primary_key.columns) == 1

        column = next(iter(primary_key.columns))

        assert column.name == "id"
        assert column.primary_key is True
        assert column.type.python_type is uuid.UUID


def test_user_structure():
    """User deve respeitar o contrato estrutural definido."""
    table = User.__table__

    assert table.c.username.nullable is False
    assert table.c.display_name.nullable is True
    assert table.c.status.nullable is False
    assert table.c.created_at.nullable is False
    assert table.c.updated_at.nullable is False

    assert any(
        constraint.name == "ck_users_status"
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    )

    assert any(
        constraint.name is None
        and "username" in {column.name for column in constraint.columns}
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    )


def test_session_structure():
    """Session deve possuir vínculo obrigatório com User."""
    table = Session.__table__

    assert table.c.user_id.nullable is False
    assert table.c.started_at.nullable is False
    assert table.c.last_activity_at.nullable is False
    assert table.c.ended_at.nullable is True
    assert table.c.status.nullable is False

    foreign_keys = list(table.c.user_id.foreign_keys)

    assert len(foreign_keys) == 1
    assert foreign_keys[0].target_fullname == "users.id"

    assert any(
        index.name == "ix_sessions_user_id"
        for index in table.indexes
    )

    assert any(
        constraint.name == "ck_sessions_status"
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    )


def test_conversation_structure():
    """Conversation deve possuir vínculo obrigatório com User."""
    table = Conversation.__table__

    assert table.c.user_id.nullable is False
    assert table.c.title.nullable is True
    assert table.c.status.nullable is False
    assert table.c.created_at.nullable is False
    assert table.c.updated_at.nullable is False

    foreign_keys = list(table.c.user_id.foreign_keys)

    assert len(foreign_keys) == 1
    assert foreign_keys[0].target_fullname == "users.id"

    assert any(
        index.name == "ix_conversations_user_id"
        for index in table.indexes
    )

    assert any(
        constraint.name == "ck_conversations_status"
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    )


def test_message_structure():
    """Message deve respeitar o contrato estrutural aprovado."""
    table = Message.__table__

    assert table.c.conversation_id.nullable is False
    assert table.c.sequence.nullable is False
    assert table.c.role.nullable is False
    assert table.c.content.nullable is False
    assert table.c.metadata.nullable is True
    assert table.c.created_at.nullable is False

    foreign_keys = list(table.c.conversation_id.foreign_keys)

    assert len(foreign_keys) == 1
    assert foreign_keys[0].target_fullname == "conversations.id"

    assert any(
        constraint.name == "uq_messages_conversation_sequence"
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    )

    assert any(
        constraint.name == "ck_messages_role"
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    )

    assert any(
        constraint.name == "ck_messages_content_not_blank"
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    )


def test_message_sequence_unique_constraint_covers_conversation():
    """
    A sequência deve ser única dentro de cada conversa.

    A mesma sequência pode existir em conversas diferentes.
    """
    constraint = next(
        constraint
        for constraint in Message.__table__.constraints
        if (
            isinstance(constraint, UniqueConstraint)
            and constraint.name == "uq_messages_conversation_sequence"
        )
    )

    assert [column.name for column in constraint.columns] == [
        "conversation_id",
        "sequence",
    ]


def test_required_foreign_keys_are_not_cascading_delete():
    """
    O domínio não permite exclusão destrutiva em cascata.
    """
    relationships = (
        (Session.__table__.c.user_id, "users.id"),
        (Conversation.__table__.c.user_id, "users.id"),
        (Message.__table__.c.conversation_id, "conversations.id"),
    )

    for column, target in relationships:
        foreign_key = next(iter(column.foreign_keys))

        assert foreign_key.target_fullname == target
        assert foreign_key.ondelete == "RESTRICT"


def test_relationships_are_defined():
    """Os relacionamentos ORM essenciais devem existir."""
    assert hasattr(User, "sessions")
    assert hasattr(User, "conversations")

    assert hasattr(Session, "user")

    assert hasattr(Conversation, "user")
    assert hasattr(Conversation, "messages")

    assert hasattr(Message, "conversation")


def test_message_metadata_uses_database_column_name():
    """
    O atributo Python metadata_ deve continuar usando a coluna física
    'metadata', evitando conflito com o atributo reservado do SQLAlchemy.
    """
    column = Message.__table__.c.metadata

    assert column.name == "metadata"