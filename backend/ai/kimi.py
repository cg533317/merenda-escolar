from backend.ai.base import AIProvider
from backend.ai.kimi_client import KimiClient
from backend.config import Config


class KimiProvider(AIProvider):
    """Provedor de inteligência artificial baseado na API do Kimi."""

    def __init__(self, api_key=None, model=None, client=None):
        self.api_key = api_key or Config.KIMI_API_KEY
        self.model = model or Config.KIMI_MODEL
        self.client = client or KimiClient(self.api_key)

    def generate(self, prompt: str) -> str:
        """Envia um prompt para o Kimi e retorna a resposta."""

        if not self.api_key:
            raise ValueError("KIMI_API_KEY não configurada.")

        return self.client.chat(
            model=self.model,
            prompt=prompt
        )
