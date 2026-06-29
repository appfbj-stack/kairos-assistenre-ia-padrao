from typing import Optional
from core.container import Container
from core.domain.entities.context import RuntimeContext


class KairosSDK:
    def __init__(self, container: Container):
        self._container = container
        self._context_key: Optional[str] = None

    @classmethod
    async def build(cls, conversation_repo=None, memory_repo=None, tool_repo=None, llm=None) -> "KairosSDK":
        container = Container(
            conversation_repo=conversation_repo,
            memory_repo=memory_repo,
            tool_repo=tool_repo,
            llm=llm,
        ).build()
        return cls(container)

    def register_context(
        self,
        key: str,
        tenant_id: str,
        tenant_name: str,
        tenant_slug: str,
        user_id: str,
        user_name: str,
        user_email: str,
        user_role: str = "member",
        app_id: str = "",
        app_name: str = "",
        app_slug: str = "",
        app_context: str = "",
    ) -> RuntimeContext:
        ctx = self._container.context_manager.build(
            tenant_id=tenant_id,
            tenant_name=tenant_name,
            tenant_slug=tenant_slug,
            user_id=user_id,
            user_name=user_name,
            user_email=user_email,
            user_role=user_role,
            app_id=app_id,
            app_name=app_name,
            app_slug=app_slug,
            app_context=app_context,
        )
        self._container.context_manager.set(key, ctx)
        self._context_key = key
        return ctx

    def update_context(self, key: str, **kwargs):
        self._container.context_manager.update(key, **kwargs)

    async def register_tool(
        self,
        app_id: str,
        name: str,
        description: str,
        parameters: list[dict],
        endpoint: str,
        method: str = "POST",
        headers: Optional[dict] = None,
    ):
        return await self._container.tool_registry.register(
            app_id=app_id,
            name=name,
            description=description,
            parameters=parameters,
            endpoint=endpoint,
            method=method,
            headers=headers,
        )

    async def list_tools(self, app_id: str):
        return await self._container.tool_registry.list_by_app(app_id)

    async def execute_tool(self, tool_name: str, app_id: str, args: dict):
        return await self._container.tool_registry.execute(tool_name, app_id, args)

    async def send_message(self, message: str, conversation_id: Optional[str] = None) -> dict:
        if not self._context_key:
            raise ValueError("Context not registered. Call register_context() first.")
        return await self._container.orchestrator.process_message(
            message=message,
            context_key=self._context_key,
            conversation_id=conversation_id,
        )

    @property
    def orchestrator(self):
        return self._container.orchestrator

    @property
    def event_bus(self):
        return self._container.event_bus
