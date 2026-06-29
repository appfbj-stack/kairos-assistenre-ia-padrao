from dataclasses import dataclass
from typing import Optional


@dataclass
class MemoryEntry:
    id: Optional[str] = None
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    key: str = ""
    value: str = ""
    type: str = "session"
    created_at: Optional[str] = None
