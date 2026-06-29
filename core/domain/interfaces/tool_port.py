from abc import ABC, abstractmethod
from typing import Optional, AsyncGenerator
from core.domain.entities.tool import ToolDef


class ToolPort(ABC):
    @abstractmethod
    async def register(self, tool: ToolDef) -> ToolDef: ...

    @abstractmethod
    async def get_by_id(self, tool_id: str) -> Optional[ToolDef]: ...

    @abstractmethod
    async def get_by_name(self, app_id: str, name: str) -> Optional[ToolDef]: ...

    @abstractmethod
    async def list_by_app(self, app_id: str) -> list[ToolDef]: ...

    @abstractmethod
    async def list_by_tenant(self, tenant_id: str) -> list[ToolDef]: ...

    @abstractmethod
    async def execute(self, tool: ToolDef, args: dict) -> dict: ...

    @abstractmethod
    async def delete(self, tool_id: str) -> None: ...
