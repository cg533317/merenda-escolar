"""
Testes de contrato do modelo Memory (FASE 6.2).

Protegem as decisÃµes estruturais da entidade Memory:
    - escopos USER / CONVERSATION;
    - origens USER_CONFIRMED / SYSTEM_CREATED / IMPORTED;
    - estados ACTIVE / SUPERSEDED / ARCHIVED;
    - invariante escopo â†” conversation_id;
    - vÃ­nculo de propriedade (owner_user_id);
    - auto-referÃªncia de superaÃ§Ã£o.
"""

import uuid

import pytest
from sqlalchemy import CheckConstraint, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as SQLAlchemySession

from backend.database.models import Base, Memory

def test_memory_table_exists():
    assert "memories" in Memory.__table__.metadata.tables


def test_memory_uuid_primary_key():
    primary_key = Memory.__table__.primary_key
    assert len(primary_key.columns) == 1
    column = next(iter(primary_key.columns))
    assert column.name == "id"
    assert column.type.python_type is uuid.UUID


def test_memory_structure():
    table = Memory.__table__

    assert table.c.owner_user_id.nullable is False
    assert table.c.conversation_id.nullable is True
    assert table.c.scope.nullable is False
    assert table.c.origin.nullable is False
    assert table.c.status.nullable is False
    assert table.c.category.nullable is True
    assert table.c.supersedes_memory_id.nullable is True
    assert table.c.content.nullable is False
    assert table.c.metadata.nullable is True
    assert table.c.created_at.nullable is False
    assert table.c.updated_at.nullable is False
    assert table.c.expires_at.nullable is True


def test_memory_foreign_keys():
    table = Memory.__table__

    owner_fk = list(table.c.owner_user_id.foreign_keys)
    assert len(owner_fk) == 1
    assert owner_fk[0].target_fullname == "users.id"
    assert owner_fk[0].ondelete == "RESTRICT"

    conversation_fk = list(table.c.conversation_id.foreign_keys)
    assert len(conversation_fk) == 1
    assert conversation_fk[0].target_fullname == "conversations.id"
    assert conversation_fk[0].ondelete == "RESTRICT"

    supersedes_fk = list(table.c.supersedes_memory_id.foreign_keys)
    assert len(supersedes_fk) == 1
    assert supersedes_fk[0].target_fullname == "memories.id"
    assert supersedes_fk[0].ondelete == "RESTRICT"


def test_memory_scope_check_constraint():
    constraint = next(
        c for c in Memory.__table__.constraints
        if isinstance(c, CheckConstraint) and c.name == "ck_memories_scope"
    )
    assert "user" in constraint.sqltext.text
    assert "conversation" in constraint.sqltext.text


def test_memory_origin_check_constraint():
    constraint = next(
        c for c in Memory.__table__.constraints
        if isinstance(c, CheckConstraint) and c.name == "ck_memories_origin"
    )
    for origin in ("user_confirmed", "system_created", "imported"):
        assert origin in constraint.sqltext.text


def test_memory_status_check_constraint():
    constraint = next(
        c for c in Memory.__table__.constraints
        if isinstance(c, CheckConstraint) and c.name == "ck_memories_status"
    )
    for status in ("active", "superseded", "archived"):
        assert status in constraint.sqltext.text


def test_memory_scope_conversation_invariant():
    """
    USER exige conversation_id NULL; CONVERSATION exige conversation_id
    presente. Impede memÃ³ria USER vinculada a conversa e vice-versa.
    """
    constraint = next(
        c for c in Memory.__table__.constraints
        if isinstance(c, CheckConstraint)
        and c.name == "ck_memories_scope_conversation"
    )
    text = constraint.sqltext.text
    assert "scope" in text
    assert "conversation_id" in text


def test_memory_content_not_blank():

    constraint = next(
        c for c in Memory.__table__.constraints
        if isinstance(c, CheckConstraint)
        and c.name == "ck_memories_content_not_blank"
    )
    assert "trim" in constraint.sqltext.text


def test_memory_not_self_superseded():
    constraint = next(
        c for c in Memory.__table__.constraints
        if isinstance(c, CheckConstraint)
        and c.name == "ck_memories_not_self_superseded"
    )
    assert "supersedes_memory_id" in constraint.sqltext.text


def test_memory_indexes():
    names = {index.name for index in Memory.__table__.indexes}
    assert "ix_memories_owner_user_id" in names
    assert "ix_memories_conversation_id" in names
    assert "ix_memories_owner_scope_status" in names


    assert Memory.__table__.c.metadata.name == "metadata"



def _create_memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


def _create_valid_memory(**overrides):
    values = {
        "id": uuid.uuid4(),
        "owner_user_id": uuid.uuid4(),
        "conversation_id": None,
        "scope": "user",
        "origin": "user_confirmed",
        "status": "active",
        "content": "MemÃ³ria vÃ¡lida",
    }
    values.update(overrides)
    return values


def test_memory_rejects_invalid_scope():
    engine = _create_memory_db()

    try:
        with SQLAlchemySession(engine) as session:
            with pytest.raises(IntegrityError):
                session.execute(Memory.__table__.insert().values(
                    **_create_valid_memory(scope="invalid"),
                ))
    finally:
        engine.dispose()


def test_memory_rejects_invalid_origin():
    engine = _create_memory_db()

    try:
        with SQLAlchemySession(engine) as session:
            with pytest.raises(IntegrityError):
                session.execute(Memory.__table__.insert().values(
                    **_create_valid_memory(origin="invalid"),
                ))
    finally:
        engine.dispose()


def test_memory_rejects_invalid_status():
    engine = _create_memory_db()

    try:
        with SQLAlchemySession(engine) as session:
            with pytest.raises(IntegrityError):
                session.execute(Memory.__table__.insert().values(
                    **_create_valid_memory(status="invalid"),
                ))
    finally:
        engine.dispose()


def test_memory_rejects_blank_content():
    engine = _create_memory_db()

    try:
        with SQLAlchemySession(engine) as session:
            with pytest.raises(IntegrityError):
                session.execute(Memory.__table__.insert().values(
                    **_create_valid_memory(content="   "),
                ))
    finally:
        engine.dispose()


def test_memory_rejects_user_scope_with_conversation():
    engine = _create_memory_db()

    try:
        with SQLAlchemySession(engine) as session:
            with pytest.raises(IntegrityError):
                session.execute(Memory.__table__.insert().values(
                    **_create_valid_memory(
                        scope="user",
                        conversation_id=uuid.uuid4(),
                    ),
                ))
    finally:
        engine.dispose()


def test_memory_rejects_conversation_scope_without_conversation():
    engine = _create_memory_db()

    try:
        with SQLAlchemySession(engine) as session:
            with pytest.raises(IntegrityError):
                session.execute(Memory.__table__.insert().values(
                    **_create_valid_memory(
                        scope="conversation",
                        conversation_id=None,
                    ),
                ))
    finally:
        engine.dispose()


def test_memory_rejects_self_supersede():
    engine = _create_memory_db()

    try:
        memory_id = uuid.uuid4()

        with SQLAlchemySession(engine) as session:
            with pytest.raises(IntegrityError):
                session.execute(Memory.__table__.insert().values(
                    **_create_valid_memory(
                        id=memory_id,
                        supersedes_memory_id=memory_id,
                    ),
                ))
    finally:
        engine.dispose()
