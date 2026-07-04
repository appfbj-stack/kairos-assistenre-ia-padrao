from typing import Optional
from core.domain.entities.app import (
    AppDef, AppModule, AppPermission, SupportedResource,
    AppStatus, AppEnvironment,
)
from core.domain.interfaces.app_port import AppPort


class AppRegistryError(Exception):
    pass


class AppRegistry:
    def __init__(self, repo: AppPort):
        self._repo = repo

    async def register(self, app: AppDef) -> AppDef:
        if not AppDef.validate_slug(app.slug):
            raise AppRegistryError(f"Invalid slug format: '{app.slug}'. Use only lowercase letters, numbers, hyphens, underscores (3-50 chars).")
        if not AppDef.validate_version(app.version):
            raise AppRegistryError(f"Invalid version format: '{app.version}'. Use semver (e.g. 1.0.0).")
        if not app.name.strip():
            raise AppRegistryError("App name is required.")
        if not app.tenant_id:
            raise AppRegistryError("Tenant ID is required.")

        existing = await self._repo.get_by_slug(app.tenant_id, app.slug)
        if existing:
            raise AppRegistryError(f"App '{app.slug}' already registered for this tenant.")

        return await self._repo.register(app)

    async def update(self, app: AppDef) -> AppDef:
        existing = await self._repo.get_by_id(app.id)
        if not existing:
            raise AppRegistryError(f"App '{app.id}' not found.")

        if app.version and not AppDef.validate_version(app.version):
            raise AppRegistryError(f"Invalid version format: '{app.version}'.")

        return await self._repo.update(app)

    async def remove(self, app_id: str) -> None:
        existing = await self._repo.get_by_id(app_id)
        if not existing:
            raise AppRegistryError(f"App '{app_id}' not found.")
        await self._repo.delete(app_id)

    async def get(self, app_id: str) -> Optional[AppDef]:
        return await self._repo.get_by_id(app_id)

    async def get_by_slug(self, tenant_id: str, slug: str) -> Optional[AppDef]:
        return await self._repo.get_by_slug(tenant_id, slug)

    async def list_by_tenant(self, tenant_id: str) -> list[AppDef]:
        return await self._repo.list_by_tenant(tenant_id)

    async def list_all(self) -> list[AppDef]:
        return await self._repo.list_all()

    async def set_status(self, app_id: str, status: str) -> None:
        try:
            AppStatus(status)
        except ValueError:
            raise AppRegistryError(f"Invalid status: '{status}'. Use: active, inactive, maintenance.")
        await self._repo.set_status(app_id, status)

    async def validate_credentials(self, api_key: str, app_slug: str) -> bool:
        from core.domain.interfaces.app_port import AppPort as AP
        pass  # Validation done at route level via resolve_tenant
