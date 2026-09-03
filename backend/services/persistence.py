"""
AquaBot — Persistência (Engine e Sessão)
========================================

Responsabilidade:
    Prover a engine e a fábrica de sessões SQLAlchemy utilizadas pela
    aplicação em produção.

Quando `DATABASE_URL` não é fornecido, utiliza um banco SQLite em
arquivo (`aquabot.db`) para permitir que a persistência funcione
end-to-end nesta fase.

A camada HTTP não conhece esta infraestrutura diretamente.
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.config import Config
from backend.database.models import Base


def _resolve_database_url() -> str:
    """Resolve a URL do banco, com fallback para SQLite em arquivo."""
    url = (Config.DATABASE_URL or "").strip()

    if url:
        return url

    project_root = Path(__file__).resolve().parents[2]
    sqlite_path = project_root / "aquabot.db"

    return f"sqlite:///{sqlite_path.as_posix()}"


def create_db_engine():
    """Cria a engine do banco de dados."""
    return create_engine(_resolve_database_url())


def create_session_factory(engine=None):
    """Cria uma fábrica de sessões vinculada à engine fornecida."""
    if engine is None:
        engine = create_db_engine()

    return sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )


def init_db(engine=None) -> None:
    """Cria as tabelas do banco, caso ainda não existam."""
    if engine is None:
        engine = create_db_engine()

    Base.metadata.create_all(engine)
