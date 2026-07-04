from fastapi import APIRouter, Depends, HTTPException, Header, Query
from fastapi import Request as Req
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Tenant
from core.domain.entities.app import (
    AppDef, AppModule, AppPermission, SupportedResource,
    AppStatus, AppEnvironment,
)
from core.application.app_registry import AppRegistryError

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


def get_registry(request: Req):
    container = request.app.state.container
    if not container.app_registry:
        raise HTTPException(status_code=503, detail="App Registry not available")
    return container.app_registry


# --- Request/Response Models ---

class ModuleSchema(BaseModel):
    name: str
    description: str = ""
    is_active: bool = True


class PermissionSchema(BaseModel):
    key: str
    name: str
    description: str = ""
    module: str = "general"


class RegisterAppRequest(BaseModel):
    name: str
    slug: str
    version: str = "1.0.0"
    company: str = ""
    api_url: str = ""
    environment: str = "production"
    icon: str = ""
    primary_color: str = "#1e40af"
    origin_url: str = ""
    context: str = ""
    modules: list[ModuleSchema] = []
    tools: list[dict] = []
    permissions: list[PermissionSchema] = []
    supported_resources: list[str] = ["voice", "image", "document"]


class UpdateAppRequest(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    company: Optional[str] = None
    api_url: Optional[str] = None
    environment: Optional[str] = None
    icon: Optional[str] = None
    primary_color: Optional[str] = None
    origin_url: Optional[str] = None
    context: Optional[str] = None
    modules: Optional[list[ModuleSchema]] = None
    permissions: Optional[list[PermissionSchema]] = None
    supported_resources: Optional[list[str]] = None
    is_active: Optional[bool] = None


class ContextRegisterRequest(BaseModel):
    app_slug: str
    app_name: str
    modules: list[str] = []
    context: str = ""


class SessionRegisterRequest(BaseModel):
    app_slug: str
    user_id: str
    user_name: str
    user_email: str
    user_role: str = "member"
    modules: list[str] = []
    departments: list[str] = []


def get_container(request: Req):
    return request.app.state.container


# --- App Registry CRUD ---

@router.post("/register")
async def register_app(
    req: RegisterAppRequest,
    request: Req,
    tenant=Depends(resolve_tenant),
):
    registry = get_registry(request)
    app = AppDef(
        id="",
        tenant_id=str(tenant.id),
        name=req.name,
        slug=req.slug,
        version=req.version,
        company=req.company,
        api_url=req.api_url,
        environment=AppEnvironment(req.environment) if req.environment else AppEnvironment.PRODUCTION,
        icon=req.icon,
        primary_color=req.primary_color,
        origin_url=req.origin_url,
        context=req.context,
        modules=[AppModule(**m.model_dump()) for m in req.modules],
        permissions=[AppPermission(**p.model_dump()) for p in req.permissions],
        supported_resources=[SupportedResource(r) for r in req.supported_resources],
    )
    try:
        result = await registry.register(app)
        return result.to_dict()
    except AppRegistryError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{app_id}")
async def update_app(
    app_id: str,
    req: UpdateAppRequest,
    request: Req,
    tenant=Depends(resolve_tenant),
):
    registry = get_registry(request)
    existing = await registry.get(app_id)
    if not existing:
        raise HTTPException(status_code=404, detail="App not found")
    if existing.tenant_id != str(tenant.id):
        raise HTTPException(status_code=403, detail="App belongs to another tenant")

    data = req.model_dump(exclude_unset=True)
    if "modules" in data and data["modules"] is not None:
        data["modules"] = [AppModule(**m) for m in data["modules"]]
    if "permissions" in data and data["permissions"] is not None:
        data["permissions"] = [AppPermission(**p) for p in data["permissions"]]
    if "supported_resources" in data and data["supported_resources"] is not None:
        data["supported_resources"] = [SupportedResource(r) for r in data["supported_resources"]]

    for field, val in data.items():
        setattr(existing, field, val)

    try:
        result = await registry.update(existing)
        return result.to_dict()
    except AppRegistryError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{app_id}")
async def remove_app(
    app_id: str,
    request: Req,
    tenant=Depends(resolve_tenant),
):
    registry = get_registry(request)
    existing = await registry.get(app_id)
    if not existing:
        raise HTTPException(status_code=404, detail="App not found")
    if existing.tenant_id != str(tenant.id):
        raise HTTPException(status_code=403, detail="App belongs to another tenant")
    await registry.remove(app_id)
    return {"removed": app_id}


@router.get("/{app_id}")
async def get_app(
    app_id: str,
    request: Req,
    tenant=Depends(resolve_tenant),
):
    registry = get_registry(request)
    app = await registry.get(app_id)
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    if app.tenant_id != str(tenant.id):
        raise HTTPException(status_code=403, detail="App belongs to another tenant")
    return app.to_dict()


@router.get("/slug/{slug}")
async def get_app_by_slug(
    slug: str,
    request: Req,
    tenant=Depends(resolve_tenant),
):
    registry = get_registry(request)
    app = await registry.get_by_slug(str(tenant.id), slug)
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    return app.to_dict()


@router.get("")
async def list_apps(
    request: Req,
    tenant=Depends(resolve_tenant),
):
    registry = get_registry(request)
    apps = await registry.list_by_tenant(str(tenant.id))
    return {"apps": [a.to_dict() for a in apps], "total": len(apps)}


@router.patch("/{app_id}/status")
async def set_app_status(
    app_id: str,
    status: str = Query(..., description="active, inactive, or maintenance"),
    request: Req = None,
    tenant=Depends(resolve_tenant),
):
    registry = get_registry(request)
    existing = await registry.get(app_id)
    if not existing:
        raise HTTPException(status_code=404, detail="App not found")
    if existing.tenant_id != str(tenant.id):
        raise HTTPException(status_code=403, detail="App belongs to another tenant")
    try:
        await registry.set_status(app_id, status)
        return {"id": app_id, "status": status}
    except AppRegistryError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Context & Session (existing) ---

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
