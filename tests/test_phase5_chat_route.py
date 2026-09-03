"""
Testes da FASE 5 — Endpoint /api/chat com persistência.

Validam o comportamento HTTP dos novos cenários:
    - conversation_id opcional e validação de UUID;
    - conversation inexistente/de outro usuário → 404;
    - conversation ended/archived → 409;
    - falha da IA → 502;
    - request antigo continua funcionando.
"""

import uuid

import pytest
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock

from backend.ai.kimi_errors import KimiAPIError
from backend.config import Config
from backend.database.models import Base
from backend.database.repositories import (
    ConversationRepository,
    MessageRepository,
    UserRepository,
)
from backend.routes.chat import create_chat_bp
from backend.services.chat_service import ChatService
from backend.services.context_policy import MostRecentContextPolicy
from backend.services.identity import TechnicalIdentityProvider


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    yield session_factory
    engine.dispose()


def _build_app(db, *, username="tester", response="Resposta", fail=False):
    provider = Mock()
    provider.metadata.return_value = {
        "provider": "KimiProvider",
        "model": "kimi-k2.6",
    }

    ai_service = Mock()
    ai_service.provider = provider
    if fail:
        ai_service.generate.side_effect = KimiAPIError("Erro simulado")
    else:
        ai_service.generate.return_value = response

    service = ChatService(
        ai_service,
        session_factory=db,
        identity_provider=TechnicalIdentityProvider(
            username=username,
            display_name="Tester",
        ),
        context_policy=MostRecentContextPolicy(max_messages=10),
    )

    app = Flask(__name__)
    app.config.from_object(Config)
    chat_bp = create_chat_bp(service, None)
    app.register_blueprint(chat_bp)
    return app


def _create_active_conversation(db, username="tester", status="active"):
    session = db()
    try:
        user = UserRepository(session).create(username=username)
        conversation = ConversationRepository(session).create(
            user_id=user.id,
            status=status,
        )
        session.commit()
        return conversation.id
    finally:
        session.close()


def test_route_chat_sem_conversation_id_retorna_conversation_id(db):
    app = _build_app(db)

    with app.test_client() as client:
        response = client.post("/api/chat", json={"message": "Olá"})

    assert response.status_code == 200
    data = response.get_json()
    assert data["conversation_id"]
    uuid.UUID(data["conversation_id"])


def test_route_chat_com_conversation_id_valido(db):
    app = _build_app(db)
    conversation_id = _create_active_conversation(db, username="tester")

    with app.test_client() as client:
        response = client.post(
            "/api/chat",
            json={
                "conversation_id": str(conversation_id),
                "message": "Continue",
            },
        )

    assert response.status_code == 200
    data = response.get_json()
    assert data["conversation_id"] == str(conversation_id)


def test_route_chat_conversation_id_invalido_retorna_400(db):
    app = _build_app(db)

    with app.test_client() as client:
        response = client.post(
            "/api/chat",
            json={"conversation_id": "nao-e-um-uuid", "message": "Olá"},
        )

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "validation_error"


def test_route_chat_conversation_inexistente_retorna_404(db):
    app = _build_app(db)

    with app.test_client() as client:
        response = client.post(
            "/api/chat",
            json={
                "conversation_id": str(uuid.uuid4()),
                "message": "Olá",
            },
        )

    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "conversation_not_found"


def test_route_chat_isolation_retorna_404_sem_revelar_existencia(db):
    # Usuário tester cria uma conversa.
    conversation_id = _create_active_conversation(db, username="tester")

    # Outro usuário (outro_usuario) tenta acessar a conversa do tester.
    app = _build_app(db, username="outro_usuario")

    with app.test_client() as client:
        response = client.post(
            "/api/chat",
            json={
                "conversation_id": str(conversation_id),
                "message": "Tentar acessar",
            },
        )

    # Não revela a existência da conversa alheia → comportamento de 404.
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "conversation_not_found"

    # Nenhuma mensagem nova foi adicionada à conversa original.
    session = db()
    try:
        messages = MessageRepository(session).list_by_conversation(conversation_id)
        assert messages == []
    finally:
        session.close()


def test_route_chat_conversation_ended_retorna_409(db):
    _create_active_conversation(db, username="tester", status="ended")
    app = _build_app(db, username="tester")

    # Recupera a conversa encerrada do usuário.
    session = db()
    try:
        user = UserRepository(session).get_by_username("tester")
        conversation = ConversationRepository(session).list_by_user(user.id)[0]
        conversation_id = conversation.id
    finally:
        session.close()

    with app.test_client() as client:
        response = client.post(
            "/api/chat",
            json={
                "conversation_id": str(conversation_id),
                "message": "Continuar",
            },
        )

    assert response.status_code == 409
    data = response.get_json()
    assert data["error"] == "conversation_not_active"


def test_route_chat_conversation_archived_retorna_409(db):
    _create_active_conversation(db, username="tester", status="archived")
    app = _build_app(db, username="tester")

    session = db()
    try:
        user = UserRepository(session).get_by_username("tester")
        conversation = ConversationRepository(session).list_by_user(user.id)[0]
        conversation_id = conversation.id
    finally:
        session.close()

    with app.test_client() as client:
        response = client.post(
            "/api/chat",
            json={
                "conversation_id": str(conversation_id),
                "message": "Continuar",
            },
        )

    assert response.status_code == 409
    data = response.get_json()
    assert data["error"] == "conversation_not_active"


def test_route_chat_ia_falha_retorna_502_e_preserva_message_user(db):
    # Nota: _build_app(fail=True) faz generate levantar KimiAPIError.
    app = _build_app(db, username="tester", fail=True)

    with app.test_client() as client:
        response = client.post(
            "/api/chat",
            json={"message": "Mensagem que falha"},
        )

    assert response.status_code == 502
    data = response.get_json()
    assert data["error"] == "provider_error"

    # Message(user) deve permanecer persistida; nenhuma assistant criada.
    session = db()
    try:
        user = UserRepository(session).get_by_username("tester")
        assert user is not None
        conversations = ConversationRepository(session).list_by_user(user.id)
        assert len(conversations) == 1
        conversation_id = conversations[0].id
        messages = MessageRepository(session).list_by_conversation(conversation_id)
        assert [msg.role for msg in messages] == ["user"]
        assert messages[0].content == "Mensagem que falha"
    finally:
        session.close()


def test_route_chat_old_request_still_works(db):
    """O request antigo {message: ...} continua funcionando com persistência."""
    app = _build_app(db)

    with app.test_client() as client:
        response = client.post("/api/chat", json={"message": "Olá"})

    assert response.status_code == 200
    data = response.get_json()
    assert data["response"] == "Resposta"
    assert data["provider"] == "KimiProvider"
    assert data["conversation_id"]
