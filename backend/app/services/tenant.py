from app.models import Tenant
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_tenant_by_api_key(db: AsyncSession, api_key: str) -> Tenant | None:
    result = await db.execute(select(Tenant).where(Tenant.api_key == api_key, Tenant.is_active == True))
    return result.scalar_one_or_none()


async def get_tenant_context(db: AsyncSession, tenant_id) -> str:
    result = await db.execute(select(Tenant.context).where(Tenant.id == tenant_id))
    row = result.scalar_one_or_none()
    return row or ""
