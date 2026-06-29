from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class AuditEntry:
    tenant_id: str
    event_type: str
    tool_name: Optional[str] = None
    app_slug: Optional[str] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    user_role: Optional[str] = None
    input_data: Optional[str] = None
    result: Optional[str] = None
    success: bool = True
    ip_address: Optional[str] = None
    id: Optional[str] = None
    created_at: Optional[str] = None


class AuditPort(ABC):
    @abstractmethod
    async def record(self, entry: AuditEntry) -> AuditEntry: ...

    @abstractmethod
    async def query(
        self,
        tenant_id: str,
        event_type: Optional[str] = None,
        user_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditEntry]: ...

    @abstractmethod
    async def count(
        self,
        tenant_id: str,
        event_type: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> int: ...
