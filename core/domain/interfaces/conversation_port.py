from abc import ABC, abstractmethod
from typing import Optional
from core.domain.entities.conversation import Conversation, Message


class ConversationPort(ABC):
    @abstractmethod
    async def create(self, conversation: Conversation) -> Conversation: ...

    @abstractmethod
    async def get_by_id(self, conversation_id: str) -> Optional[Conversation]: ...

    @abstractmethod
    async def add_message(self, message: Message) -> Message: ...

    @abstractmethod
    async def get_messages(self, conversation_id: str) -> list[Message]: ...

    @abstractmethod
    async def list_by_tenant(self, tenant_id: str, limit: int = 50) -> list[Conversation]: ...

    @abstractmethod
    async def delete(self, conversation_id: str) -> None: ...
