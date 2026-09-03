from flask import Flask

from backend.config import Config
from backend.routes.health import health_bp
from backend.ai.factory import ProviderFactory, ProviderFactoryError
from backend.services.ai_service import AIService
from backend.services.chat_service import ChatService
from backend.services.context_policy import MostRecentContextPolicy
from backend.services.identity import TechnicalIdentityProvider
from backend.services.persistence import (
    create_db_engine,
    create_session_factory,
    init_db,
)
from backend.routes.chat import create_chat_bp


def create_app():
    """Cria e configura a aplicação AquaBot com composition root."""

    app = Flask(__name__)
    app.config.from_object(Config)

    # Composition Root - criar dependências
    chat_service = None
    initialization_error = None

    try:
        provider = ProviderFactory.create()
        ai_service = AIService(provider)
        db_engine = create_db_engine()
        init_db(db_engine)
        session_factory = create_session_factory(db_engine)
        identity_provider = TechnicalIdentityProvider()
        context_policy = MostRecentContextPolicy(
            max_messages=Config.CONTEXT_HISTORY_MESSAGES,
        )
        chat_service = ChatService(
            ai_service,
            session_factory=session_factory,
            identity_provider=identity_provider,
            context_policy=context_policy,
        )
    except Exception as e:
        # Armazena erro mas permite que app inicie
        initialization_error = str(e)
        app.logger.error(f"Failed to initialize AI services: {e}")

    # Sempre registrar blueprint - endpoint deve existir
    chat_bp = create_chat_bp(chat_service, initialization_error)
    app.register_blueprint(chat_bp)

    app.register_blueprint(health_bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=app.config["DEBUG"]
    )
