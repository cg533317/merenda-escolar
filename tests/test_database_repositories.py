"""
Testes dos Repositories de persistência do AquaBot.

Nesta etapa validamos o comportamento da camada de persistência
sobre um banco SQLite temporário em memória.
"""

import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.orm import sessionmaker

from backend.database.models import Base
from backend.database.repositories import (
    ConversationRepository,
    MessageRepository,
    SessionRepository,
    UserRepository,
)


@pytest.fixture
def db_session():
    """Cria um banco SQLite isolado para cada teste."""
    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(engine)

    session_factory = sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

    session = session_factory()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_user_repository_create_and_find(db_session: SQLAlchemySession):
    repository = UserRepository(db_session)

    user = repository.create(
        username="carlos",
        display_name="Carlos",
    )

    db_session.commit()

    assert user.id is not None
    assert isinstance(user.id, uuid.UUID)
    assert user.username == "carlos"
    assert user.display_name == "Carlos"
    assert user.status == "active"

    found_by_id = repository.get_by_id(user.id)
    found_by_username = repository.get_by_username("carlos")

    assert found_by_id is user
    assert found_by_username is user


def test_user_repository_returns_none_when_user_does_not_exist(
    db_session: SQLAlchemySession,
):
    repository = UserRepository(db_session)

    random_id = uuid.uuid4()

    assert repository.get_by_id(random_id) is None
    assert repository.get_by_username("inexistente") is None


def test_session_repository_lifecycle(db_session: SQLAlchemySession):
    user_repository = UserRepository(db_session)
    session_repository = SessionRepository(db_session)

    user = user_repository.create(username="usuario")
    db_session.commit()

    session = session_repository.create(user_id=user.id)

    assert session.user_id == user.id
    assert session.status == "active"
    assert session.started_at is not None
    assert session.last_activity_at is not None
    assert session.ended_at is None

    original_activity = session.last_activity_at

    session_repository.update_activity(session)

    assert session.last_activity_at >= original_activity

    session_repository.end(session)

    assert session.status == "ended"
    assert session.ended_at is not None


def test_conversation_repository_create_and_list_by_user(
    db_session: SQLAlchemySession,
):
    user_repository = UserRepository(db_session)
    conversation_repository = ConversationRepository(db_session)

    user = user_repository.create(username="usuario")

    conversation_1 = conversation_repository.create(
        user_id=user.id,
        title="Primeira conversa",
    )

    conversation_2 = conversation_repository.create(
        user_id=user.id,
        title="Segunda conversa",
    )

    other_user = user_repository.create(username="outro")

    other_conversation = conversation_repository.create(
        user_id=other_user.id,
        title="Outra conversa",
    )

    db_session.commit()

    found = conversation_repository.get_by_id(conversation_1.id)

    assert found is conversation_1

    conversations = conversation_repository.list_by_user(user.id)

    assert conversations == [conversation_1, conversation_2]
    assert other_conversation not in conversations


def test_message_repository_creates_sequential_messages(
    db_session: SQLAlchemySession,
):
    user_repository = UserRepository(db_session)
    conversation_repository = ConversationRepository(db_session)
    message_repository = MessageRepository(db_session)

    user = user_repository.create(username="usuario")

    conversation = conversation_repository.create(
        user_id=user.id,
        title="Teste",
    )

    message_1 = message_repository.create(
        conversation_id=conversation.id,
        role="user",
        content="Olá",
    )

    message_2 = message_repository.create(
        conversation_id=conversation.id,
        role="assistant",
        content="Olá! Como posso ajudar?",
    )

    db_session.commit()

    assert message_1.sequence == 1
    assert message_2.sequence == 2

    assert message_repository.get_last_sequence(
        conversation.id
    ) == 2


def test_message_repository_lists_messages_in_sequence_order(
    db_session: SQLAlchemySession,
):
    user_repository = UserRepository(db_session)
    conversation_repository = ConversationRepository(db_session)
    message_repository = MessageRepository(db_session)

    user = user_repository.create(username="usuario")

    conversation = conversation_repository.create(
        user_id=user.id,
    )

    message_repository.create(
        conversation_id=conversation.id,
        role="user",
        content="Primeira",
    )

    message_repository.create(
        conversation_id=conversation.id,
        role="assistant",
        content="Segunda",
    )

    message_repository.create(
        conversation_id=conversation.id,
        role="user",
        content="Terceira",
    )

    db_session.commit()

    messages = message_repository.list_by_conversation(
        conversation.id
    )

    assert [message.sequence for message in messages] == [1, 2, 3]
    assert [message.content for message in messages] == [
        "Primeira",
        "Segunda",
        "Terceira",
    ]


def test_message_repository_get_by_id(
    db_session: SQLAlchemySession,
):
    user_repository = UserRepository(db_session)
    conversation_repository = ConversationRepository(db_session)
    message_repository = MessageRepository(db_session)

    user = user_repository.create(username="usuario")

    conversation = conversation_repository.create(
        user_id=user.id,
    )

    message = message_repository.create(
        conversation_id=conversation.id,
        role="user",
        content="Mensagem",
        metadata={"source": "test"},
    )

    db_session.commit()

    found = message_repository.get_by_id(message.id)

    assert found is message
    assert found.metadata_ == {"source": "test"}


def test_message_repository_empty_conversation(
    db_session: SQLAlchemySession,
):
    user_repository = UserRepository(db_session)
    conversation_repository = ConversationRepository(db_session)
    message_repository = MessageRepository(db_session)

    user = user_repository.create(username="usuario")

    conversation = conversation_repository.create(
        user_id=user.id,
    )

    db_session.commit()

    assert (
        message_repository.get_last_sequence(conversation.id)
        == 0
    )

    assert (
        message_repository.list_by_conversation(conversation.id)
        == []
    )


def test_repositories_do_not_commit_implicitly(
    db_session: SQLAlchemySession,
):
    """
    Os Repositories não devem controlar o commit da transação.

    A aplicação deve poder agrupar várias operações em uma única
    transação.
    """
    repository = UserRepository(db_session)

    user = repository.create(username="sem-commit")

    assert user in db_session.new
    assert db_session.new

    db_session.rollback()

    assert repository.get_by_username("sem-commit") is None


def test_invalid_message_content_is_rejected(
    db_session: SQLAlchemySession,
):
    user_repository = UserRepository(db_session)
    conversation_repository = ConversationRepository(db_session)
    message_repository = MessageRepository(db_session)

    user = user_repository.create(username="usuario")

    conversation = conversation_repository.create(
        user_id=user.id,
    )

    message = message_repository.create(
        conversation_id=conversation.id,
        role="user",
        content="   ",
    )

    db_session.add(message)

    with pytest.raises(Exception):
        db_session.commit()

    db_session.rollback()