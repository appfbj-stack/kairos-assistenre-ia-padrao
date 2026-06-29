from abc import ABC, abstractmethod
from typing import Optional
from core.domain.entities.memory import MemoryEntry


class MemoryPort(ABC):
    @abstractmethod
    async def store(self, entry: MemoryEntry) -> MemoryEntry: ...

    @abstractmethod
    async def get(self, key: str, user_id: Optional[str] = None, tenant_id: Optional[str] = None) -> Optional[str]: ...

    @abstractmethod
    async def list_by_type(self, type: str, user_id: Optional[str] = None, tenant_id: Optional[str] = None) -> list[MemoryEntry]: ...

    @abstractmethod
    async def delete(self, key: str, user_id: Optional[str] = None) -> None: ...

    @abstractmethod
    async def clear_session(self, user_id: str) -> None: ...
