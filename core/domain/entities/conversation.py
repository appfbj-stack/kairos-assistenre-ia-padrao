from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


@dataclass
class Message:
    role: MessageRole
    content: str
    id: Optional[str] = None
    conversation_id: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    created_at: Optional[str] = None


@dataclass
class Conversation:
    id: str
    tenant_id: str
    app_id: Optional[str] = None
    user_id: Optional[str] = None
    title: str = "Nova conversa"
    messages: list[Message] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def add_message(self, message: Message):
        message.conversation_id = self.id
        self.messages.append(message)

    def to_llm_history(self) -> list[dict]:
        return [
            {"role": m.role.value, "content": m.content}
            for m in self.messages
            if m.role in (MessageRole.USER, MessageRole.ASSISTANT, MessageRole.TOOL)
        ]
