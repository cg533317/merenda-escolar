import pytest

from backend.ai.base import AIProvider
from backend.ai.kimi import KimiProvider


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

    with pytest.raises(ValueError, match="KIMI_API_KEY não configurada"):
        provider.generate("Olá AquaBot")


def test_kimi_provider_does_not_call_api_yet():
    provider = KimiProvider(api_key="chave-de-teste")

    with pytest.raises(NotImplementedError, match="API do Kimi"):
        provider.generate("Olá AquaBot")
