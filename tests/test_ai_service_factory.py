from backend.ai.factory import ProviderFactory
from backend.services.ai_service import AIService


def test_ai_service_with_factory_created_provider():
    provider = ProviderFactory.create("kimi")
    service = AIService(provider)
    
    assert service.provider is not None
    assert service.provider.__class__.__name__ == "KimiProvider"


def test_ai_service_generates_with_factory_provider():
    from backend.ai.base import AIProvider
    
    class MockProvider(AIProvider):
        def generate(self, prompt: str) -> str:
            return f"Mock response: {prompt}"
    
    ProviderFactory.register_provider("mock", MockProvider)
    provider = ProviderFactory.create("mock")
    service = AIService(provider)
    
    result = service.generate("test prompt")
    
    assert result == "Mock response: test prompt"


if __name__ == "__main__":
    test_ai_service_with_factory_created_provider()
    test_ai_service_generates_with_factory_provider()
    print("AIService with Factory tests passed")