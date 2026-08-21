import requests

from backend.ai.base import AIProvider
from backend.config import Config


class KimiProvider(AIProvider):
    """Provedor de inteligência artificial baseado na API do Kimi."""

    def __init__(self, api_key=None):
        self.api_key = api_key or Config.KIMI_API_KEY

    def generate(self, prompt: str) -> str:
        """Envia um prompt para o Kimi e retorna a resposta."""
        if not self.api_key:
            raise ValueError("KIMI_API_KEY não configurada.")

        raise NotImplementedError(
            "Integração com a API do Kimi ainda não foi implementada."
        )
