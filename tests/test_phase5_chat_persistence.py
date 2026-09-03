"""
Testes da FASE 5 — Integração Conversacional Persistente.

Cobrem os cenários obrigatórios:
    - nova conversa;
    - continuação;
    - isolamento de dados entre usuários;
    - conversation inexistente;
    - conversation encerrada/arquivada;
    - falha da IA;
    - persistência (metadata, timestamps, sequência);
    - compatibilidade (request antigo);
    - segurança (sem segredos/prompt em logs).
"""

import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock

from backend.ai.kimi_errors import KimiAPIError
from backend.database.models import Base
from backend.database.repositories import (
    ConversationRepository,
    MessageRepository,
    UserRepository,
)
from backend.services.chat_service import (
    ChatService,
    ConversationNotFoundError,
    ConversationNotActiveError,
)
from backend.services.context_policy import MostRecentContextPolicy
from backend.services.identity import TechnicalIdentityProvider


@pytest.fixture
def db():
    """Cria um banco SQLite isolado e a fábrica de sessões para cada teste."""
    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(engine)

    session_factory = sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

    yield session_factory

    engine.dispose()


def _provider_mock(provider_name="KimiProvider", model="kimi-k2.6"):
    provider = Mock()
    provider.metadata.return_value = {
        "provider": provider_name,
        "model": model,
    }
    return provider


def _make_service(
    db,
    username="tester",
    response="Resposta simulada",
    max_messages=10,
):
    provider = _provider_mock()
    ai_service = Mock()
    ai_service.provider = provider
    ai_service.generate.return_value = response

    identity = TechnicalIdentityProvider(
        username=username,
        display_name="Tester",
    )
    context = MostRecentContextPolicy(max_messages=max_messages)

    return ChatService(
        ai_service,
        session_factory=db,
        identity_provider=identity,
        context_policy=context,
    )


def _count_messages(session_factory, conversation_id):
    session = session_factory()
    try:
        repo = MessageRepository(session)
        return repo.list_by_conversation(conversation_id)
    finally:
        session.close()


# ------------------------------------------------------------------
# Nova conversa
# ------------------------------------------------------------------
def test_new_conversation_creates_and_returns_conversation_id(db):
    service = _make_service(db)

    result = service.process("Olá, AquaBot")

    assert "conversation_id" in result
    conversation_uuid = uuid.UUID(result["conversation_id"])
    assert result["response"] == "Resposta simulada"
    assert result["provider"] == "KimiProvider"
    assert result["model"] == "kimi-k2.6"

    session = db()
    try:
        user_repo = UserRepository(session)
        conv_repo = ConversationRepository(session)
        user = user_repo.get_by_username("tester")
        assert user is not None

        conv = conv_repo.get_by_id(conversation_uuid)
        assert conv is not None
        assert conv.user_id == user.id
        assert conv.status == "active"

        messages = MessageRepository(session).list_by_conversation(conversation_uuid)
        assert [msg.role for msg in messages] == ["user", "assistant"]
        assert [msg.sequence for msg in messages] == [1, 2]
        assert messages[0].content == "Olá, AquaBot"
        assert messages[1].content == "Resposta simulada"
    finally:
        session.close()


def test_new_conversation_does_not_create_duplicate(db):
    service = _make_service(db)

    service.process("Primeira")
    service.process("Segunda")

    session = db()
    try:
        user = UserRepository(session).get_by_username("tester")
        conversations = ConversationRepository(session).list_by_user(user.id)

        assert len(conversations) == 2
    finally:
        session.close()


# ------------------------------------------------------------------
# Continuação
# ------------------------------------------------------------------
def test_continuation_uses_history_and_continues_sequence(db):
    service = _make_service(db, response="Resposta nova")

    first = service.process("Primeira pergunta")
    conversation_uuid = uuid.UUID(first["conversation_id"])

    # Captura o prompt enviado na segunda chamada
    second = service.process(
        "Continue nossa conversa",
        conversation_id=first["conversation_id"],
    )

    assert second["conversation_id"] == first["conversation_id"]

    # O histórico deve ter sido incluído no contexto enviado à IA
    prompts = [
        call.args[0] if call.args else call.kwargs.get("prompt")
        for call in service.ai_service.generate.call_args_list
    ]
    assert len(prompts) == 2
    assert "Primeira pergunta" in prompts[1]

    messages = _count_messages(db, conversation_uuid)
    assert [msg.role for msg in messages] == [
        "user",
        "assistant",
        "user",
        "assistant",
    ]
    assert [msg.sequence for msg in messages] == [1, 2, 3, 4]


def test_continuation_without_history_just_passes_message(db):
    service = _make_service(db, response="Resp")

    result = service.process("Só uma mensagem")

    prompts = [call.args[0] for call in service.ai_service.generate.call_args_list]
    assert len(prompts) == 1
    # A mensagem do usuário faz parte do contexto construído
    assert "Só uma mensagem" in prompts[0]


# ------------------------------------------------------------------
# Isolamento de dados
# ------------------------------------------------------------------
def test_user_cannot_access_other_users_conversation(db):
    service_a = _make_service(db, username="user_a")
    service_b = _make_service(db, username="user_b")

    result_a = service_a.process("Mensagem do A")

    with pytest.raises(ConversationNotFoundError):
        service_b.process(
            "Tentar acessar",
            conversation_id=result_a["conversation_id"],
        )

    # Nenhuma mensagem falsa deve ter sido criada na conversa de A
    messages = _count_messages(db, uuid.UUID(result_a["conversation_id"]))
    assert len(messages) == 2  # apenas user + assistant originais


# ------------------------------------------------------------------
# Conversation inexistente
# ------------------------------------------------------------------
def test_conversation_inexistente_raises_not_found(db):
    service = _make_service(db)

    with pytest.raises(ConversationNotFoundError):
        service.process(
            "Mensagem",
            conversation_id=str(uuid.uuid4()),
        )

    # Não deve criar dados indevidos para o usuário
    session = db()
    try:
        assert UserRepository(session).get_by_username("tester") is None
    finally:
        session.close()


# ------------------------------------------------------------------
# Conversation encerrada
# ------------------------------------------------------------------
def test_conversation_ended_cannot_be_reused(db):
    session = db()
    try:
        user_repo = UserRepository(session)
        conv_repo = ConversationRepository(session)
        user = user_repo.create(username="tester")
        conversation = conv_repo.create(user_id=user.id)
        conv_repo.update_status(conversation, "ended")
        conversation_id = conversation.id
        session.commit()
    finally:
        session.close()

    service = _make_service(db)

    with pytest.raises(ConversationNotActiveError):
        service.process(
            "Continuar",
            conversation_id=str(conversation_id),
        )

    # Nenhuma nova mensagem deve ter sido criada
    assert _count_messages(db, conversation_id) == []


# ------------------------------------------------------------------
# Conversation arquivada
# ------------------------------------------------------------------
def test_conversation_archived_cannot_be_reused(db):
    session = db()
    try:
        user_repo = UserRepository(session)
        conv_repo = ConversationRepository(session)
        user = user_repo.create(username="tester")
        conversation = conv_repo.create(user_id=user.id)
        conv_repo.update_status(conversation, "archived")
        conversation_id = conversation.id
        session.commit()
    finally:
        session.close()

    service = _make_service(db)

    with pytest.raises(ConversationNotActiveError):
        service.process(
            "Continuar",
            conversation_id=str(conversation_id),
        )

    assert _count_messages(db, conversation_id) == []


# ------------------------------------------------------------------
# Falha da IA
# ------------------------------------------------------------------
def test_ai_failure_preserves_user_message_and_skips_assistant(db):
    provider = _provider_mock()
    ai_service = Mock()
    ai_service.provider = provider
    ai_service.generate.side_effect = KimiAPIError("Erro simulado")

    identity = TechnicalIdentityProvider(username="tester")
    context = MostRecentContextPolicy(max_messages=10)

    service = ChatService(
        ai_service,
        session_factory=db,
        identity_provider=identity,
        context_policy=context,
    )

    with pytest.raises(KimiAPIError):
        service.process("Mensagem que falha")

    session = db()
    try:
        user_repo = UserRepository(session)
        conv_repo = ConversationRepository(session)
        user = user_repo.get_by_username("tester")
        conversations = conv_repo.list_by_user(user.id)

        assert len(conversations) == 1
        conversation_id = conversations[0].id

        messages = MessageRepository(session).list_by_conversation(conversation_id)
        assert [msg.role for msg in messages] == ["user"]
        assert messages[0].content == "Mensagem que falha"
    finally:
        session.close()


# ------------------------------------------------------------------
# Persistência: metadata, timestamps, sequência
# ------------------------------------------------------------------
def test_persistence_metadata_and_timestamps(db):
    service = _make_service(db)

    result = service.process("Olá")

    conversation_uuid = uuid.UUID(result["conversation_id"])

    session = db()
    try:
        messages = MessageRepository(session).list_by_conversation(conversation_uuid)
        user_msg, assistant_msg = messages

        assert user_msg.metadata_ is None
        assert assistant_msg.metadata_ == {
            "provider": "KimiProvider",
            "model": "kimi-k2.6",
        }

        assert user_msg.created_at is not None
        assert assistant_msg.created_at is not None
        assert assistant_msg.created_at >= user_msg.created_at
    finally:
        session.close()


# ------------------------------------------------------------------
# Compatibilidade: request antigo continua funcionando
# ------------------------------------------------------------------
def test_legacy_mode_without_persistence_still_works():
    """Sem persistência, o comportamento original é preservado."""
    provider = _provider_mock()
    ai_service = Mock()
    ai_service.provider = provider
    ai_service.generate.return_value = "Resposta"

    service = ChatService(ai_service)

    result = service.process("Olá")

    assert result["response"] == "Resposta"
    ai_service.generate.assert_called_once_with("Olá")
    assert "conversation_id" not in result


# ------------------------------------------------------------------
# Segurança
# ------------------------------------------------------------------
def test_metadata_never_contains_secrets(db):
    service = _make_service(db)

    result = service.process("Olá")

    conversation_uuid = uuid.UUID(result["conversation_id"])

    session = db()
    try:
        messages = MessageRepository(session).list_by_conversation(conversation_uuid)
        for message in messages:
            metadata = message.metadata_ or {}
            assert "api_key" not in str(metadata).lower()
            assert "secret" not in str(metadata).lower()
            assert "token" not in str(metadata).lower()
    finally:
        session.close()
