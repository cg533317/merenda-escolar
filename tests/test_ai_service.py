import pytest

from backend.ai.base import AIProvider
from backend.services.ai_service import AIService


class FakeAIProvider(AIProvider):
    def __init__(self):
        self.prompt = None

    def generate(self, prompt: str) -> str:
        self.prompt = prompt
        return "Resposta simulada da IA"


def test_ai_service_uses_provider():
    provider = FakeAIProvider()
    service = AIService(provider)

    result = service.generate("Olá AquaBot")

    assert result == "Resposta simulada da IA"
    assert provider.prompt == "Olá AquaBot"


def test_ai_service_requires_provider():
    with pytest.raises(ValueError, match="provedor de IA"):
        AIService(None)
