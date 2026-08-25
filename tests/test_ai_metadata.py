from backend.ai.base import AIProvider


class TestProvider(AIProvider):
    def generate(self, prompt: str) -> str:
        return f"Response: {prompt}"


def test_ai_provider_has_metadata_method():
    provider = TestProvider()
    
    assert hasattr(provider, 'metadata')
    assert callable(provider.metadata)


def test_ai_provider_metadata_returns_dict():
    provider = TestProvider()
    
    metadata = provider.metadata()
    
    assert isinstance(metadata, dict)


def test_ai_provider_metadata_includes_provider_name():
    provider = TestProvider()
    
    metadata = provider.metadata()
    
    assert "provider" in metadata
    assert metadata["provider"] == "TestProvider"


def test_ai_provider_metadata_default_implementation():
    provider = TestProvider()
    
    metadata = provider.metadata()
    
    assert len(metadata) >= 1
    assert "provider" in metadata


if __name__ == "__main__":
    test_ai_provider_has_metadata_method()
    test_ai_provider_metadata_returns_dict()
    test_ai_provider_metadata_includes_provider_name()
    test_ai_provider_metadata_default_implementation()
    print("AIProvider metadata tests passed")