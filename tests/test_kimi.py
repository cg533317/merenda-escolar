from backend.ai.base import AIProvider
from backend.ai.kimi import KimiProvider


class FakeKimiClient:
    def __init__(self):
        self.model = None
        self.prompt = None

    def chat(self, model, prompt):
        self.model = model
        self.prompt = prompt

        return "Resposta simulada do Kimi"


def test_kimi_provider_implements_ai_provider():
    provider = KimiProvider(api_key="chave-de-teste")

    assert isinstance(provider, AIProvider)
    assert provider.api_key == "chave-de-teste"
    assert provider.model == "kimi-k2.6"


def test_kimi_provider_accepts_custom_model():
    provider = KimiProvider(
        api_key="chave-de-teste",
        model="modelo-de-teste"
    )

    assert provider.model == "modelo-de-teste"


def test_kimi_provider_requires_api_key():
    provider = KimiProvider(api_key="")

    assert provider.api_key == ""

    try:
        provider.generate("Olá AquaBot")
    except ValueError as error:
        assert str(error) == "KIMI_API_KEY não configurada."
    else:
        raise AssertionError("Era esperado ValueError")


def test_kimi_provider_uses_kimi_client():
    fake_client = FakeKimiClient()

    provider = KimiProvider(
        api_key="chave-de-teste",
        model="kimi-k2.6",
        client=fake_client
    )

    result = provider.generate("Olá AquaBot")

    assert result == "Resposta simulada do Kimi"
    assert fake_client.model == "kimi-k2.6"
    assert fake_client.prompt == "Olá AquaBot"
