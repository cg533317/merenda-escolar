from backend.config import Config


class AppService:
    """Serviços relacionados às informações da aplicação."""

    @staticmethod
    def get_info():
        return {
            "name": Config.APP_NAME,
            "environment": Config.APP_ENV,
            "debug": Config.DEBUG
        }
