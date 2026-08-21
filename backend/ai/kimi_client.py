import requests

from backend.ai.kimi_errors import KimiAPIError


class KimiClient:
    """Cliente HTTP para comunicação com a API do Kimi."""

    BASE_URL = "https://api.moonshot.ai/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def chat(self, model: str, prompt: str) -> str:
        """Envia uma mensagem para a API do Kimi."""

        if not self.api_key:
            raise KimiAPIError("KIMI_API_KEY não configurada.")

        url = f"{self.BASE_URL}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=60,
            )

            response.raise_for_status()

        except requests.RequestException as error:
            raise KimiAPIError(
                f"Erro na comunicação com a API do Kimi: {error}"
            ) from error

        data = response.json()

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise KimiAPIError(
                "Resposta inválida recebida da API do Kimi."
            ) from error
