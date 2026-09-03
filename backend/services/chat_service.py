from uuid import UUID

from backend.ai.kimi_errors import KimiAPIError
from backend.database.repositories import (
    ConversationRepository,
    MessageRepository,
    UserRepository,
)

class ConversationNotFoundError(Exception):
    """Conversation inexistente ou de outro usuário (recurso não encontrado)."""


class ConversationNotActiveError(Exception):
    """Conversation não está ativa (ended/archived) e não pode ser reutilizada."""


class ChatService:
    """Serviço responsável pela lógica de chat do AquaBot.

    Orquestra o fluxo conversacional persistente:

        Route
          ↓
        ChatService
          ├── Repositories → SQLAlchemy Models
          └── AIService → AIProvider → KimiClient

    A camada HTTP não conhece SQLAlchemy. O KimiClient/KimiProvider/AIService
    não conhecem persistência.
    """

    def __init__(
        self,
        ai_service,
        session_factory=None,
        identity_provider=None,
        context_policy=None,
    ):
        """
        Inicializa o ChatService.

        Args:
            ai_service: Instância de AIService já configurada.
            session_factory: Fábrica de sessões do banco (persistência).
                Quando None, o serviço opera no modo legado, sem persistir.
            identity_provider: Resolve a identidade do usuário atual.
                Quando None, a persistência fica desativada.
            context_policy: Política de construção de contexto a partir do
                histórico. Quando None, a persistência fica desativada.
        """
        self.ai_service = ai_service
        self.session_factory = session_factory
        self.identity_provider = identity_provider
        self.context_policy = context_policy

    def _persistence_enabled(self) -> bool:
        return (
            self.session_factory is not None
            and self.identity_provider is not None
            and self.context_policy is not None
        )

    def _provider_metadata(self) -> dict:
        provider_metadata = self.ai_service.provider.metadata()
        return {
            "provider": provider_metadata.get("provider"),
            "model": provider_metadata.get("model"),
        }

    def _resolve_or_create_user(self, user_repo: UserRepository) -> object:
        username = self.identity_provider.get_username()
        display_name = self.identity_provider.get_display_name()

        user = user_repo.get_by_username(username)

        if user is None:
            user = user_repo.create(
                username=username,
                display_name=display_name,
            )

        return user

    def _build_prompt(self, context: str, message: str) -> str:
        """Constrói o prompt contextualizado a partir do histórico.

        O contexto já inclui a mensagem atual do usuário como último turno.
        O sufixo "Assistente:" orienta o provedor a produzir a resposta.
        """
        if not context.strip():
            return message

        return (
            "Histórico da conversa:\n"
            f"{context}\n"
            "\n"
            "Assistente:"
        )

    def _process_legacy(self, message: str) -> dict:
        """Comportamento original sem persistência (retrocompatível)."""
        response = self.ai_service.generate(message)
        provider_metadata = self.ai_service.provider.metadata()

        return {
            "response": response,
            "provider": provider_metadata.get("provider"),
            "model": provider_metadata.get("model"),
        }

    def process(
        self,
        message: str,
        model: str = None,
        conversation_id=None,
    ) -> dict:
        """
        Processa uma mensagem de chat, persistindo o fluxo conversacional.

        Args:
            message: Mensagem do usuário.
            model: Modelo específico (opcional).
            conversation_id: UUID da conversation a continuar. Quando None,
                cria uma nova Conversation.

        Returns:
            Dicionário com a resposta e o conversation_id.

        Raises:
            KimiAPIError: Se houver erro na comunicação com o provider.
            ConversationNotFoundError: Conversation inexistente ou de outro
                usuário (além da verificação de identidade).
            ConversationNotActiveError: Conversation ended/archived.
        """
        if not self._persistence_enabled():
            return self._process_legacy(message)

        if conversation_id is not None and not isinstance(conversation_id, UUID):
            try:
                conversation_id = UUID(str(conversation_id))
            except (ValueError, AttributeError):
                raise ConversationNotFoundError(
                    "Conversation não encontrada."
                )

        # --- Transação 1: identidade, conversa e mensagem do usuário ---
        user_message = None
        history = []
        conversation = None

        session = self.session_factory()
        try:
            user_repo = UserRepository(session)
            conversation_repo = ConversationRepository(session)
            message_repo = MessageRepository(session)

            user = self._resolve_or_create_user(user_repo)

            if conversation_id is None:
                conversation = conversation_repo.create(user_id=user.id)
            else:
                conversation = conversation_repo.get_by_id_for_user(
                    conversation_id,
                    user.id,
                )

                if conversation is None:
                    raise ConversationNotFoundError(
                        "Conversation não encontrada."
                    )

                if conversation.status != "active":
                    raise ConversationNotActiveError(
                        f"Conversation {conversation.status}."
                    )

            history = message_repo.list_by_conversation(conversation.id)

            user_message = message_repo.create(
                conversation_id=conversation.id,
                role="user",
                content=message,
            )

            session.commit()

        except ConversationNotFoundError:
            session.rollback()
            raise

        except ConversationNotActiveError:
            session.rollback()
            raise

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()

        # --- Construção do contexto e prompt (sem transação de banco aberta) ---
        context_messages = history + [user_message]
        context = self.context_policy.build_context(context_messages)
        prompt = self._build_prompt(context, message)

        # --- Chamada à IA (fora da transação de banco) ---
        provider_metadata = self._provider_metadata()
        response = self.ai_service.generate(prompt)

        # --- Transação 2: mensagem da IA e atualização da Conversation ---
        conversation_id_value = conversation.id

        session = self.session_factory()
        try:
            conversation_repo = ConversationRepository(session)
            message_repo = MessageRepository(session)

            updated_conversation = conversation_repo.get_by_id(
                conversation_id_value
            )

            message_repo.create(
                conversation_id=conversation_id_value,
                role="assistant",
                content=response,
                metadata=provider_metadata,
            )

            conversation_repo.update(updated_conversation)

            session.commit()

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()

        return {
            "conversation_id": str(conversation_id_value),
            "response": response,
            "provider": provider_metadata.get("provider"),
            "model": provider_metadata.get("model"),
        }
