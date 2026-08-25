from backend.ai.base import AIProvider
from backend.ai.kimi import KimiProvider
from backend.config import Config


class ProviderFactoryError(Exception):
    """Erro relacionado à criação de providers de IA."""
    pass


class ProviderFactory:
    """Factory para criação de providers de IA baseados em configuração."""

    _providers = {
        "kimi": KimiProvider,
    }

    @classmethod
    def create(cls, provider_name: str = None) -> AIProvider:
        """
        Cria uma instância de provider de IA baseado na configuração.
        
        Args:
            provider_name: Nome do provider (ex: "kimi"). 
                          Se None, usa a configuração padrão.
        
        Returns:
            Instância de AIProvider configurada.
        
        Raises:
            ProviderFactoryError: Se o provider não for reconhecido.
        """
        if provider_name is None:
            provider_name = Config.AI_PROVIDER

        provider_class = cls._providers.get(provider_name.lower())

        if provider_class is None:
            available = ", ".join(cls._providers.keys())
            raise ProviderFactoryError(
                f"Provider '{provider_name}' não reconhecido. "
                f"Providers disponíveis: {available}"
            )

        return provider_class()

    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """
        Registra um novo provider na factory.
        
        Args:
            name: Nome do provider.
            provider_class: Classe do provider (deve herdar de AIProvider).
        """
        if not issubclass(provider_class, AIProvider):
            raise ProviderFactoryError(
                f"Provider class must inherit from AIProvider"
            )
        
        cls._providers[name.lower()] = provider_class