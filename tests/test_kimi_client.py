import pytest

from backend.ai.kimi_client import KimiClient
from backend.ai.kimi_errors import KimiAPIError


class FakeResponse:
    def raise_for_status(self):
        pass

    def json(self):
        return {
            "choices": [
                {
                    "message": {
                        "content": "Resposta simulada do Kimi"
                    }
                }
            ]
        }


def test_kimi_client_requires_api_key():
    client = KimiClient(api_key="")

    with pytest.raises(KimiAPIError, match="KIMI_API_KEY não configurada"):
        client.chat(
            model="kimi-k2.6",
            prompt="Olá AquaBot"
        )


def test_kimi_client_chat(monkeypatch):
    client = KimiClient(api_key="chave-de-teste")

    captured = {}

    def fake_post(url, headers, json, timeout):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout

        return FakeResponse()

    monkeypatch.setattr(
        "backend.ai.kimi_client.requests.post",
        fake_post
    )

    result = client.chat(
        model="kimi-k2.6",
        prompt="Olá AquaBot"
    )

    assert result == "Resposta simulada do Kimi"

    assert captured["url"] == (
        "https://api.moonshot.ai/v1/chat/completions"
    )

    assert captured["headers"]["Authorization"] == (
        "Bearer chave-de-teste"
    )

    assert captured["json"]["model"] == "kimi-k2.6"

    assert captured["json"]["messages"] == [
        {
            "role": "user",
            "content": "Olá AquaBot"
        }
    ]

    assert captured["timeout"] == 60


def test_kimi_client_converts_http_error_to_kimi_error(monkeypatch):
    client = KimiClient(api_key="chave-de-teste")

    def fake_post(*args, **kwargs):
        raise __import__("requests").RequestException(
            "erro simulado"
        )

    monkeypatch.setattr(
        "backend.ai.kimi_client.requests.post",
        fake_post
    )

    with pytest.raises(
        KimiAPIError,
        match="Erro na comunicação com a API do Kimi"
    ):
        client.chat(
            model="kimi-k2.6",
            prompt="Olá AquaBot"
        )


def test_kimi_client_rejects_invalid_response(monkeypatch):
    client = KimiClient(api_key="chave-de-teste")

    class InvalidResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {}

    monkeypatch.setattr(
        "backend.ai.kimi_client.requests.post",
        lambda *args, **kwargs: InvalidResponse()
    )

    with pytest.raises(
        KimiAPIError,
        match="Resposta inválida recebida da API do Kimi"
    ):
        client.chat(
            model="kimi-k2.6",
            prompt="Olá AquaBot"
        )
