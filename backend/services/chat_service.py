from backend.ai.kimi_errors import KimiAPIError


class ChatService:
    """Serviço responsável pela lógica de chat do AquaBot."""

    def __init__(self, ai_service):
        """
        Inicializa o ChatService.
        
        Args:
            ai_service: Instância de AIService já configurada.
        """
        self.ai_service = ai_service

    def process(self, message: str, model: str = None) -> dict:
        """
        Processa uma mensagem de chat e retorna a resposta.
        
        Args:
            message: Mensagem do usuário.
            model: Modelo específico (opcional).
        
        Returns:
            Dicionário com os dados da resposta.
        
        Raises:
            KimiAPIError: Se houver erro na comunicação com o provider.
        """
        response = self.ai_service.generate(message)
        
        # Obter metadados do provider através do AIService
        provider_metadata = self.ai_service.provider.metadata()
        
        return {
            "response": response,
            "provider": provider_metadata.get("provider"),
            "model": provider_metadata.get("model"),
        }
