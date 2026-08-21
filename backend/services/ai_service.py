from backend.ai.base import AIProvider


class AIService:
    """Serviço responsável por intermediar o uso de provedores de IA."""

    def __init__(self, provider: AIProvider):
        if provider is None:
            raise ValueError("provedor de IA não configurado.")

        self.provider = provider

    def generate(self, prompt: str) -> str:
        """Gera uma resposta utilizando o provedor configurado."""
        return self.provider.generate(prompt)
