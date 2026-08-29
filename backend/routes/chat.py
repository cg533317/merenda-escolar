from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from typing import Optional
from backend.core.logging import get_logger
from backend.ai.kimi_errors import KimiAPIError
from backend.config import Config

logger = get_logger("AquaBot")


def create_chat_bp(chat_service: Optional['ChatService'], initialization_error: Optional[str] = None):
    """
    Factory function para criar blueprint com dependências injetadas.
    
    Args:
        chat_service: Instância de ChatService ou None se inicialização falhou.
        initialization_error: Mensagem de erro se inicialização falhou.
    
    Returns:
        Blueprint Flask configurado.
    """
    bp = Blueprint('chat', __name__, url_prefix='/api')
    
    @bp.route('/chat', methods=['POST'])
    def chat():
        """Endpoint POST /api/chat para processar mensagens de chat."""
        
        # Se houve erro de inicialização, retornar 500 imediatamente
        if initialization_error:
            logger.error(f"AI services initialization failed: {initialization_error}")
            return jsonify({
                "error": "internal_error",
                "message": "Erro interno do servidor."
            }), 500
        
        # Validar Content-Type
        if not request.is_json:
            return jsonify({
                "error": "validation_error",
                "message": "Content-Type deve ser application/json."
            }), 400
        
        # Obter dados do request
        request_data = request.get_json()
        
        # Validar campo message
        if "message" not in request_data:
            return jsonify({
                "error": "validation_error",
                "message": "O campo 'message' é obrigatório."
            }), 400
        
        message = request_data["message"]
        
        # Validar que message é string
        if not isinstance(message, str):
            return jsonify({
                "error": "validation_error",
                "message": "O campo 'message' deve ser uma string."
            }), 400
        
        # Validar que message não está vazio
        if not message.strip():
            return jsonify({
                "error": "validation_error",
                "message": "O campo 'message' não pode estar vazio."
            }), 400
        
        # Validar tamanho da mensagem
        if len(message) > Config.CHAT_MAX_MESSAGE_LENGTH:
            return jsonify({
                "error": "validation_error",
                "message": f"O campo 'message' não pode exceder {Config.CHAT_MAX_MESSAGE_LENGTH} caracteres."
            }), 400
        
        # Validar model se fornecido
        model = request_data.get("model")
        if model is not None:
            if not isinstance(model, str) or not model.strip():
                return jsonify({
                    "error": "validation_error",
                    "message": "O campo 'model' deve ser uma string não vazia."
                }), 400
            
            if model != Config.KIMI_MODEL:
                return jsonify({
                    "error": "validation_error",
                    "message": f"O modelo '{model}' não é permitido. Use '{Config.KIMI_MODEL}'."
                }), 400
        
        # Log do request (sem expor conteúdo da mensagem)
        message_length = len(message)
        logger.info(
            f"endpoint=/api/chat method=POST message_length={message_length} model={model or Config.KIMI_MODEL}"
        )
        
        try:
            # Processar via ChatService
            result = chat_service.process(message, model)
            
            # Adicionar timestamp (responsabilidade da camada HTTP)
            result["timestamp"] = datetime.now(timezone.utc).isoformat()
            
            # Log do response
            logger.info(
                f"endpoint=/api/chat status=200 provider={result.get('provider')} model={result.get('model')}"
            )
            
            return jsonify(result), 200
            
        except KimiAPIError as e:
            # Qualquer erros da API do Kimi → 502
            logger.error(f"provider_error: {type(e).__name__}")
            return jsonify({
                "error": "provider_error",
                "message": "Não foi possível obter resposta do provedor de IA."
            }), 502
            
        except Exception as e:
            # Erro inesperado → 500
            logger.error(f"internal_error: {type(e).__name__}")
            return jsonify({
                "error": "internal_error",
                "message": "Erro interno do servidor."
            }), 500
    
    return bp
