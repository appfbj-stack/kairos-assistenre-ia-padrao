from core.domain.interfaces.audit_port import AuditPort, AuditEntry
from core.application.event_bus import InMemoryEventBus
from core.domain.entities.event import Event, EventType
import json


class AuditManager:
    def __init__(self, repo: AuditPort, event_bus: InMemoryEventBus):
        self._repo = repo
        event_bus.subscribe(EventType.TOOL_EXECUTED.value, self._on_tool_executed)
        event_bus.subscribe(EventType.TOOL_FAILED.value, self._on_tool_failed)
        event_bus.subscribe(EventType.ERROR.value, self._on_error)

    async def _on_tool_executed(self, event: Event):
        data = event.data
        await self._repo.record(AuditEntry(
            tenant_id=data.get("tenant_id", ""),
            user_id=data.get("user_id"),
            user_name=data.get("user_name"),
            user_role=data.get("user_role"),
            event_type="tool.executed",
            tool_name=data.get("tool_name"),
            app_slug=data.get("app_slug"),
            input_data=json.dumps(data.get("input", {}), ensure_ascii=False) if data.get("input") else None,
            result=json.dumps(data.get("result", {}), ensure_ascii=False) if data.get("result") else None,
            success=True,
            ip_address=data.get("ip_address"),
        ))

    async def _on_tool_failed(self, event: Event):
        data = event.data
        await self._repo.record(AuditEntry(
            tenant_id=data.get("tenant_id", ""),
            user_id=data.get("user_id"),
            user_name=data.get("user_name"),
            user_role=data.get("user_role"),
            event_type="tool.failed",
            tool_name=data.get("tool_name"),
            app_slug=data.get("app_slug"),
            input_data=json.dumps(data.get("input", {}), ensure_ascii=False) if data.get("input") else None,
            result=str(data.get("error", "")),
            success=False,
            ip_address=data.get("ip_address"),
        ))

    async def _on_error(self, event: Event):
        data = event.data
        await self._repo.record(AuditEntry(
            tenant_id=data.get("tenant_id", "system"),
            event_type="error",
            result=str(data.get("error", "Unknown error")),
            success=False,
        ))

    async def record(self, tenant_id: str, event_type: str, **kwargs) -> AuditEntry:
        entry = AuditEntry(tenant_id=tenant_id, event_type=event_type, **kwargs)
        return await self._repo.record(entry)

    async def query(self, tenant_id: str, **filters) -> list[AuditEntry]:
        return await self._repo.query(tenant_id=tenant_id, **filters)

    async def count(self, tenant_id: str, **filters) -> int:
        return await self._repo.count(tenant_id=tenant_id, **filters)
