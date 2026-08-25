from abc import ABC, abstractmethod
from typing import Dict, Any


class AIProvider(ABC):
    """Contrato base para provedores de inteligência artificial."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Gera uma resposta a partir de um prompt."""
        raise NotImplementedError

    def metadata(self) -> Dict[str, Any]:
        """
        Retorna metadados sobre o provider.
        
        Método opcional que pode ser sobrescrito por providers específicos
        para fornecer informações sobre configuração e capacidades.
        
        Returns:
            Dicionário com metadados do provider.
        """
        return {
            "provider": self.__class__.__name__,
        }
