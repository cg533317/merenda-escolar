from flask import Flask

from backend.config import Config
from backend.routes.health import health_bp


def create_app():
    """Cria e configura a aplicação AquaBot."""

    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(health_bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=app.config["DEBUG"]
    )
