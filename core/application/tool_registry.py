from typing import Optional
from core.domain.entities.tool import ToolDef, ToolParameter, ToolCategory
from core.domain.interfaces.tool_port import ToolPort
from core.domain.entities.event import Event, EventType


class ToolRegistry:
    def __init__(self, repo: ToolPort, publish_event: callable = None):
        self._repo = repo
        self._publish = publish_event

    async def register(
        self,
        app_id: str,
        name: str,
        description: str,
        parameters: list[dict],
        endpoint: str,
        method: str = "POST",
        category: str = "general",
        headers: dict | None = None,
    ) -> ToolDef:
        tool = ToolDef(
            id="",
            app_id=app_id,
            name=name,
            description=description,
            parameters=[ToolParameter(**p) for p in parameters],
            category=ToolCategory(category),
            endpoint=endpoint,
            method=method,
            headers=headers or {},
        )
        result = await self._repo.register(tool)
        if self._publish:
            await self._publish(Event(EventType.TOOL_EXECUTED, {"tool_name": name, "app_id": app_id}))
        return result

    async def list_by_app(self, app_id: str) -> list[ToolDef]:
        return await self._repo.list_by_app(app_id)

    async def list_by_tenant(self, tenant_id: str) -> list[ToolDef]:
        return await self._repo.list_by_tenant(tenant_id)

    async def execute(self, tool_name: str, app_id: str, args: dict, audit_context: dict | None = None) -> dict:
        tool = await self._repo.get_by_name(app_id, tool_name)
        if not tool:
            if self._publish:
                await self._publish(Event(EventType.TOOL_FAILED, {
                    "tool_name": tool_name, "error": "not found", **(audit_context or {}),
                }))
            raise ValueError(f"Tool '{tool_name}' not found")
        try:
            result = await self._repo.execute(tool, args)
            if self._publish:
                await self._publish(Event(EventType.TOOL_EXECUTED, {
                    "tool_name": tool_name, "result": result, "input": args, **(audit_context or {}),
                }))
            return result
        except Exception as e:
            if self._publish:
                await self._publish(Event(EventType.TOOL_FAILED, {
                    "tool_name": tool_name, "error": str(e), "input": args, **(audit_context or {}),
                }))
            raise

    def to_openai_tools(self, tools: list[ToolDef]) -> list[dict]:
        return [t.to_openai_schema() for t in tools]
