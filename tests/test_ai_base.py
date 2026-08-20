from backend.ai.base import AIProvider


class TestProvider(AIProvider):
    def generate(self, prompt: str) -> str:
        return f"Resposta de teste: {prompt}"


def test_provider():
    provider = TestProvider()

    result = provider.generate("Olá AquaBot")

    assert result == "Resposta de teste: Olá AquaBot"


if __name__ == "__main__":
    test_provider()
    print("AIProvider: contrato funcionando")
