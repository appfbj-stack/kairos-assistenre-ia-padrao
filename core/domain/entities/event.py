from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EventType(str, Enum):
    CONVERSATION_STARTED = "conversation.started"
    MESSAGE_SENT = "message.sent"
    MESSAGE_RECEIVED = "message.received"
    TOOL_EXECUTED = "tool.executed"
    TOOL_FAILED = "tool.failed"
    AGENT_TRIGGERED = "agent.triggered"
    AGENT_COMPLETED = "agent.completed"
    LLM_CALLED = "llm.called"
    LLM_RESPONDED = "llm.responded"
    ERROR = "error"
    CONTEXT_CHANGED = "context.changed"
    MEMORY_STORED = "memory.stored"
    MEMORY_RETRIEVED = "memory.retrieved"


@dataclass
class Event:
    type: EventType
    data: dict = field(default_factory=dict)
    source: str = ""
    timestamp: float = 0.0
