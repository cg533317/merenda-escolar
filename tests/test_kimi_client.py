import pytest

from backend.ai.kimi_client import KimiClient


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

    with pytest.raises(ValueError, match="KIMI_API_KEY não configurada"):
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
