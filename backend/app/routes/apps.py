from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi import Request as Req
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Tenant

router = APIRouter(prefix="/api/apps", tags=["apps"])


async def resolve_tenant(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing API key")
    api_key = authorization[7:]
    result = await db.execute(
        select(Tenant).where(Tenant.api_key == api_key, Tenant.is_active == True)
    )
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return tenant


class ContextRegisterRequest(BaseModel):
    app_slug: str
    app_name: str
    modules: list[str] = []
    context: str = ""


def get_container(request: Req):
    return request.app.state.container


@router.post("/context")
async def register_app_context(
    req: ContextRegisterRequest,
    request: Req,
    tenant=Depends(resolve_tenant),
    db: AsyncSession = Depends(get_db),
):
    from app.models import App
    result = await db.execute(
        select(App).where(App.tenant_id == tenant.id, App.slug == req.app_slug)
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")

    container = get_container(request)
    context_key = f"app:{tenant.id}:{req.app_slug}"
    ctx = container.context_manager.build(
        tenant_id=str(tenant.id),
        tenant_name=tenant.name,
        tenant_slug=tenant.slug,
        user_id="system",
        user_name="System",
        user_email="system@kairos.local",
        user_role="admin",
        app_id=str(app.id),
        app_name=req.app_name,
        app_slug=req.app_slug,
        app_context=req.context,
        modules=req.modules,
    )
    container.context_manager.set(context_key, ctx)
    return {"context_key": context_key, "app_slug": req.app_slug, "modules": req.modules}


class SessionRegisterRequest(BaseModel):
    app_slug: str
    user_id: str
    user_name: str
    user_email: str
    user_role: str = "member"
    modules: list[str] = []
    departments: list[str] = []


@router.post("/session")
async def register_session(
    req: SessionRegisterRequest,
    request: Req,
    tenant=Depends(resolve_tenant),
    db: AsyncSession = Depends(get_db),
):
    from app.models import App
    result = await db.execute(
        select(App).where(App.tenant_id == tenant.id, App.slug == req.app_slug)
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")

    container = get_container(request)
    context_key = f"user:{tenant.id}:{req.app_slug}:{req.user_id}"
    ctx = container.context_manager.build(
        tenant_id=str(tenant.id),
        tenant_name=tenant.name,
        tenant_slug=tenant.slug,
        user_id=req.user_id,
        user_name=req.user_name,
        user_email=req.user_email,
        user_role=req.user_role,
        app_id=str(app.id),
        app_name=app.name,
        app_slug=req.app_slug,
        modules=req.modules,
        departments=req.departments,
    )
    container.context_manager.set(context_key, ctx)
    return {
        "context_key": context_key,
        "user_id": req.user_id,
        "user_role": req.user_role,
        "modules": req.modules,
    }
