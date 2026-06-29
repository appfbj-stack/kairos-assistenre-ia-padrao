from typing import Optional
from core.domain.entities.memory import MemoryEntry
from core.domain.interfaces.memory_port import MemoryPort
from core.domain.entities.event import Event, EventType


class MemoryManager:
    def __init__(self, repo: MemoryPort, publish_event: callable = None):
        self._repo = repo
        self._publish = publish_event

    async def store_conversation(self, conversation_id: str, data: str, user_id: str, tenant_id: str):
        entry = MemoryEntry(
            conversation_id=conversation_id,
            user_id=user_id,
            tenant_id=tenant_id,
            key=f"conv:{conversation_id}",
            value=data,
            type="conversation",
        )
        result = await self._repo.store(entry)
        if self._publish:
            await self._publish(Event(EventType.MEMORY_STORED, {"key": entry.key, "type": "conversation"}))
        return result

    async def store_session(self, key: str, value: str, user_id: str, tenant_id: str):
        entry = MemoryEntry(
            user_id=user_id,
            tenant_id=tenant_id,
            key=f"session:{key}",
            value=value,
            type="session",
        )
        return await self._repo.store(entry)

    async def store_preference(self, key: str, value: str, user_id: str, tenant_id: str):
        entry = MemoryEntry(
            user_id=user_id,
            tenant_id=tenant_id,
            key=f"pref:{key}",
            value=value,
            type="preference",
        )
        return await self._repo.store(entry)

    async def store_long_term(self, key: str, value: str, user_id: str, tenant_id: str):
        entry = MemoryEntry(
            user_id=user_id,
            tenant_id=tenant_id,
            key=f"long:{key}",
            value=value,
            type="long_term",
        )
        return await self._repo.store(entry)

    async def get(self, key: str, user_id: Optional[str] = None, tenant_id: Optional[str] = None) -> Optional[str]:
        return await self._repo.get(key, user_id, tenant_id)

    async def get_session_memory(self, user_id: str) -> list[MemoryEntry]:
        return await self._repo.list_by_type("session", user_id=user_id)

    async def get_preferences(self, user_id: str) -> list[MemoryEntry]:
        return await self._repo.list_by_type("preference", user_id=user_id)

    async def clear_session(self, user_id: str):
        await self._repo.clear_session(user_id)
