from flask import Flask

from backend.config import Config
from backend.routes.health import health_bp
from backend.ai.factory import ProviderFactory, ProviderFactoryError
from backend.services.ai_service import AIService
from backend.services.chat_service import ChatService
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
        chat_service = ChatService(ai_service)
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
