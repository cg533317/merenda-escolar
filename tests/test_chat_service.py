import pytest
from unittest.mock import Mock
from backend.ai.kimi_errors import KimiAPIError
from backend.services.chat_service import ChatService


def test_chat_service_initialization():
    """Testa que ChatService requer ai_service."""
    ai_service = Mock()
    chat_service = ChatService(ai_service)
    
    assert chat_service.ai_service is ai_service


def test_chat_service_requires_ai_service():
    """Testa que ChatService requer ai_service válido."""
    # Python não levanta TypeError automaticamente para None sem type hints
    # Verificamos que se ai_service for None, usá-lo falhará
    ai_service = None
    chat_service = ChatService(ai_service)
    
    # Tentar usar o serviço falhará
    with pytest.raises(AttributeError):
        chat_service.process("Olá")


def test_chat_service_calls_ai_service():
    """Testa que ChatService chama AIService.generate()."""
    ai_service = Mock()
    ai_service.generate.return_value = "Resposta simulada"
    
    chat_service = ChatService(ai_service)
    result = chat_service.process("Olá AquaBot")
    
    ai_service.generate.assert_called_once_with("Olá AquaBot")
    assert result["response"] == "Resposta simulada"


def test_chat_service_propagates_kimi_error():
    """Testa que ChatService propaga erros do AIService."""
    ai_service = Mock()
    ai_service.generate.side_effect = KimiAPIError("Erro simulado")
    
    chat_service = ChatService(ai_service)
    
    with pytest.raises(KimiAPIError):
        chat_service.process("Olá AquaBot")


def test_chat_service_with_model():
    """Testa que ChatService passa model (se fornecido) e obtém metadados."""
    ai_service = Mock()
    ai_service.generate.return_value = "Resposta simulada"
    
    # Mock do provider com metadata
    provider_mock = Mock()
    provider_mock.metadata.return_value = {
        "provider": "KimiProvider",
        "model": "kimi-k2.6",
        "api_configured": True,
    }
    ai_service.provider = provider_mock
    
    chat_service = ChatService(ai_service)
    result = chat_service.process("Olá AquaBot", model="kimi-k2.6")
    
    assert result["response"] == "Resposta simulada"
    assert result["provider"] == "KimiProvider"
    assert result["model"] == "kimi-k2.6"


def test_chat_service_without_model():
    """Testa que ChatService funciona sem model e obtém metadados."""
    ai_service = Mock()
    ai_service.generate.return_value = "Resposta simulada"
    
    # Mock do provider com metadata
    provider_mock = Mock()
    provider_mock.metadata.return_value = {
        "provider": "KimiProvider",
        "model": "kimi-k2.6",
        "api_configured": True,
    }
    ai_service.provider = provider_mock
    
    chat_service = ChatService(ai_service)
    result = chat_service.process("Olá AquaBot")
    
    assert result["response"] == "Resposta simulada"
    assert result["provider"] == "KimiProvider"
    assert result["model"] == "kimi-k2.6"


def test_chat_service_no_flask_dependency():
    """Testa que ChatService não depende de Flask."""
    # Verifica que não há import de Flask no código fonte
    with open('backend/services/chat_service.py', 'r') as f:
        code = f.read()
    
    assert 'flask' not in code.lower(), "ChatService não deve importar Flask"
    assert 'Flask' not in code, "ChatService não deve importar Flask"


def test_chat_service_no_environment_access():
    """Testa que ChatService não acessa variáveis de ambiente."""
    # Verifica que não há acesso a variáveis de ambiente no código fonte
    with open('backend/services/chat_service.py', 'r') as f:
        code = f.read()
    
    assert 'os.getenv' not in code, "ChatService não deve acessar os.getenv"
    assert 'os.environ' not in code, "ChatService não deve acessar os.environ"
    assert 'import os' not in code, "ChatService não deve importar os"
