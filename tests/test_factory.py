import pytest
from backend.ai.base import AIProvider
from backend.ai.factory import ProviderFactory, ProviderFactoryError
from backend.ai.kimi import KimiProvider


class FakeProvider(AIProvider):
    def generate(self, prompt: str) -> str:
        return f"Fake: {prompt}"


def test_factory_creates_kimi_provider():
    provider = ProviderFactory.create("kimi")
    
    assert isinstance(provider, KimiProvider)
    assert provider.__class__.__name__ == "KimiProvider"


def test_factory_uses_default_config():
    provider = ProviderFactory.create()
    
    assert isinstance(provider, AIProvider)


def test_factory_rejects_unknown_provider():
    with pytest.raises(ProviderFactoryError, match="não reconhecido"):
        ProviderFactory.create("unknown_provider")


def test_factory_error_message_includes_available_providers():
    try:
        ProviderFactory.create("unknown")
    except ProviderFactoryError as e:
        assert "kimi" in str(e).lower()


def test_factory_registers_new_provider():
    ProviderFactory.register_provider("fake", FakeProvider)
    
    provider = ProviderFactory.create("fake")
    
    assert isinstance(provider, FakeProvider)
    assert provider.generate("test") == "Fake: test"


def test_factory_registration_requires_ai_provider_subclass():
    class NotAProvider:
        pass
    
    with pytest.raises(ProviderFactoryError, match="inherit from AIProvider"):
        ProviderFactory.register_provider("invalid", NotAProvider)


def test_factory_case_insensitive():
    provider1 = ProviderFactory.create("KIMI")
    provider2 = ProviderFactory.create("kimi")
    
    assert type(provider1) == type(provider2)


def test_factory_metadata_from_created_provider():
    provider = ProviderFactory.create("kimi")
    
    metadata = provider.metadata()
    
    assert "provider" in metadata
    assert metadata["provider"] == "KimiProvider"


if __name__ == "__main__":
    test_factory_creates_kimi_provider()
    test_factory_uses_default_config()
    test_factory_rejects_unknown_provider()
    test_factory_error_message_includes_available_providers()
    test_factory_registers_new_provider()
    test_factory_registration_requires_ai_provider_subclass()
    test_factory_case_insensitive()
    test_factory_metadata_from_created_provider()
    print("ProviderFactory tests passed")