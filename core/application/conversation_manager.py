from typing import Optional
from core.domain.entities.conversation import Conversation, Message, MessageRole
from core.domain.interfaces.conversation_port import ConversationPort


class ConversationManager:
    def __init__(self, repo: ConversationPort):
        self._repo = repo

    async def create(self, tenant_id: str, app_id: Optional[str] = None, user_id: Optional[str] = None, title: str = "Nova conversa") -> Conversation:
        import uuid
        conv = Conversation(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            app_id=app_id,
            user_id=user_id,
            title=title,
        )
        return await self._repo.create(conv)

    async def get(self, conversation_id: str) -> Optional[Conversation]:
        return await self._repo.get_by_id(conversation_id)

    async def add_message(self, conversation_id: str, role: MessageRole, content: str) -> Message:
        msg = Message(role=role, content=content, conversation_id=conversation_id)
        return await self._repo.add_message(msg)

    async def get_history(self, conversation_id: str) -> list[Message]:
        return await self._repo.get_messages(conversation_id)

    async def list(self, tenant_id: str, limit: int = 50) -> list[Conversation]:
        return await self._repo.list_by_tenant(tenant_id, limit)

    async def add_user_message(self, conversation_id: str, content: str) -> Message:
        return await self.add_message(conversation_id, MessageRole.USER, content)

    async def add_assistant_message(self, conversation_id: str, content: str) -> Message:
        return await self.add_message(conversation_id, MessageRole.ASSISTANT, content)
