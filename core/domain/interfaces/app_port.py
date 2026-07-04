from abc import ABC, abstractmethod
from typing import Optional
from core.domain.entities.app import AppDef


class AppPort(ABC):
    @abstractmethod
    async def register(self, app: AppDef) -> AppDef: ...

    @abstractmethod
    async def get_by_id(self, app_id: str) -> Optional[AppDef]: ...

    @abstractmethod
    async def get_by_slug(self, tenant_id: str, slug: str) -> Optional[AppDef]: ...

    @abstractmethod
    async def list_by_tenant(self, tenant_id: str) -> list[AppDef]: ...

    @abstractmethod
    async def list_all(self) -> list[AppDef]: ...

    @abstractmethod
    async def update(self, app: AppDef) -> AppDef: ...

    @abstractmethod
    async def delete(self, app_id: str) -> None: ...

    @abstractmethod
    async def set_status(self, app_id: str, status: str) -> None: ...
