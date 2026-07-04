from typing import Optional
from core.domain.entities.app import (
    AppDef, AppModule, AppPermission, SupportedResource,
    AppStatus, AppEnvironment,
)
from core.domain.interfaces.app_port import AppPort
from sqlalchemy import select, update


class SQLAlchemyAppRepo(AppPort):
    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def register(self, app: AppDef) -> AppDef:
        async with self._session_factory() as session:
            from app.models import App as AppModel
            row = AppModel(
                tenant_id=app.tenant_id,
                name=app.name,
                slug=app.slug,
                version=app.version,
                company=app.company,
                api_url=app.api_url,
                environment=app.environment.value if hasattr(app.environment, "value") else app.environment,
                icon=app.icon,
                primary_color=app.primary_color,
                status=app.status.value if hasattr(app.status, "value") else app.status,
                origin_url=app.origin_url,
                context=app.context,
                modules=[{"name": m.name if hasattr(m, "name") else m["name"] if isinstance(m, dict) else m, "description": m.description if hasattr(m, "description") else "", "is_active": m.is_active if hasattr(m, "is_active") else True} for m in app.modules],
                permissions=[{"key": p.key if hasattr(p, "key") else p["key"] if isinstance(p, dict) else p, "name": p.name if hasattr(p, "name") else "", "description": p.description if hasattr(p, "description") else "", "module": p.module if hasattr(p, "module") else "general"} for p in app.permissions],
                supported_resources=[r.value if hasattr(r, "value") else r for r in app.supported_resources],
            )
            session.add(row)
            await session.commit()
            app.id = str(row.id)
            app.created_at = str(row.created_at) if row.created_at else None
            app.updated_at = str(row.updated_at) if row.updated_at else None
            return app

    async def get_by_id(self, app_id: str) -> Optional[AppDef]:
        async with self._session_factory() as session:
            from app.models import App as AppModel
            result = await session.execute(select(AppModel).where(AppModel.id == app_id))
            row = result.scalar_one_or_none()
            return self._row_to_app(row) if row else None

    async def get_by_slug(self, tenant_id: str, slug: str) -> Optional[AppDef]:
        async with self._session_factory() as session:
            from app.models import App as AppModel
            result = await session.execute(
                select(AppModel).where(AppModel.tenant_id == tenant_id, AppModel.slug == slug)
            )
            row = result.scalar_one_or_none()
            return self._row_to_app(row) if row else None

    async def list_by_tenant(self, tenant_id: str) -> list[AppDef]:
        async with self._session_factory() as session:
            from app.models import App as AppModel
            result = await session.execute(
                select(AppModel).where(AppModel.tenant_id == tenant_id).order_by(AppModel.name)
            )
            return [self._row_to_app(r) for r in result.scalars().all()]

    async def list_all(self) -> list[AppDef]:
        async with self._session_factory() as session:
            from app.models import App as AppModel
            result = await session.execute(
                select(AppModel).order_by(AppModel.name)
            )
            return [self._row_to_app(r) for r in result.scalars().all()]

    async def update(self, app: AppDef) -> AppDef:
        async with self._session_factory() as session:
            from app.models import App as AppModel
            values = {}
            for field in ["name", "slug", "version", "company", "api_url", "environment",
                          "icon", "primary_color", "status", "origin_url", "context", "is_active"]:
                val = getattr(app, field, None)
                if val is not None:
                    if field == "environment":
                        values[field] = val.value if hasattr(val, "value") else val
                    elif field == "status":
                        values[field] = val.value if hasattr(val, "value") else val
                    else:
                        values[field] = val
            if app.modules is not None:
                values["modules"] = [{"name": m.name, "description": m.description, "is_active": m.is_active} for m in app.modules]
            if app.permissions is not None:
                values["permissions"] = [{"key": p.key, "name": p.name, "description": p.description, "module": p.module} for p in app.permissions]
            if app.supported_resources is not None:
                values["supported_resources"] = [
                    r.value if hasattr(r, "value") else r for r in app.supported_resources
                ]

            await session.execute(
                update(AppModel).where(AppModel.id == app.id).values(**values)
            )
            await session.commit()
            return await self.get_by_id(app.id)

    async def delete(self, app_id: str) -> None:
        async with self._session_factory() as session:
            from app.models import App as AppModel, Tool as ToolModel
            result = await session.execute(select(AppModel).where(AppModel.id == app_id))
            row = result.scalar_one_or_none()
            if row:
                await session.execute(
                    select(ToolModel).where(ToolModel.app_id == app_id)
                )
                await session.delete(row)
                await session.commit()

    async def set_status(self, app_id: str, status: str) -> None:
        async with self._session_factory() as session:
            from app.models import App as AppModel
            await session.execute(
                update(AppModel).where(AppModel.id == app_id).values(status=status)
            )
            await session.commit()

    def _row_to_app(self, row) -> AppDef:
        raw_modules = row.modules or []
        raw_permissions = row.permissions or []
        raw_resources = row.supported_resources or []

        return AppDef(
            id=str(row.id),
            tenant_id=str(row.tenant_id),
            name=row.name,
            slug=row.slug,
            version=row.version or "1.0.0",
            company=row.company or "",
            api_url=row.api_url or "",
            environment=AppEnvironment(row.environment) if row.environment and row.environment in [e.value for e in AppEnvironment] else AppEnvironment.PRODUCTION,
            icon=row.icon or "",
            primary_color=row.primary_color or "#1e40af",
            status=AppStatus(row.status) if row.status and row.status in [s.value for s in AppStatus] else AppStatus.ACTIVE,
            origin_url=row.origin_url or "",
            context=row.context or "",
            modules=[AppModule(**m) for m in raw_modules] if raw_modules else [],
            permissions=[AppPermission(**p) for p in raw_permissions] if raw_permissions else [],
            supported_resources=[SupportedResource(r) for r in raw_resources if r in [sr.value for sr in SupportedResource]] if raw_resources else [],
            is_active=row.is_active,
            created_at=str(row.created_at) if row.created_at else None,
            updated_at=str(row.updated_at) if row.updated_at else None,
        )
