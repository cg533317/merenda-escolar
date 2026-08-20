from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Contrato base para provedores de inteligência artificial."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Gera uma resposta a partir de um prompt."""
        raise NotImplementedError
