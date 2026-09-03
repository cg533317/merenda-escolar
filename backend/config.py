import os

from dotenv import load_dotenv


# Carrega as variáveis do arquivo .env
load_dotenv()


class Config:
    """Configurações centrais do AquaBot."""

    APP_NAME = os.getenv("APP_NAME", "AquaBot")
    APP_ENV = os.getenv("APP_ENV", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    SECRET_KEY = os.getenv("SECRET_KEY", "")

    AI_PROVIDER = os.getenv("AI_PROVIDER", "kimi")

    KIMI_API_KEY = os.getenv("KIMI_API_KEY", "")
    KIMI_MODEL = os.getenv("KIMI_MODEL", "kimi-k2.6")

    CHAT_MAX_MESSAGE_LENGTH = int(os.getenv("CHAT_MAX_MESSAGE_LENGTH", "10000"))

    OTHER_AI_API_KEY = os.getenv("OTHER_AI_API_KEY", "")

    DATABASE_URL = os.getenv("DATABASE_URL", "")

    TECHNICAL_USERNAME = os.getenv("TECHNICAL_USERNAME", "tech-user")
    TECHNICAL_DISPLAY_NAME = os.getenv("TECHNICAL_DISPLAY_NAME", "Usuário Técnico")
    CONTEXT_HISTORY_MESSAGES = int(os.getenv("CONTEXT_HISTORY_MESSAGES", "10"))
