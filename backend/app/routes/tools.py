from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, Field
from core.container import Container
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Tenant
from fastapi import Request

router = APIRouter(prefix="/api/tools", tags=["tools"])


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


class RegisterAppRequest(BaseModel):
    name: str
    slug: str
    origin_url: str = ""
    context: str = ""


class RegisterToolRequest(BaseModel):
    app_slug: str
    name: str
    description: str = ""
    tool_schema: dict = Field(default={}, validation_alias="schema")
    endpoint: str
    method: str = "POST"
    headers: dict = {}


class ExecuteToolRequest(BaseModel):
    tool_name: str
    arguments: dict = {}
    app_id: str = ""


@router.post("/apps/register")
async def register_app(
    req: RegisterAppRequest,
    tenant=Depends(resolve_tenant),
    db: AsyncSession = Depends(get_db),
):
    from app.models import App
    existing = await db.execute(
        select(App).where(App.tenant_id == tenant.id, App.slug == req.slug)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="App slug already exists")
    app = App(tenant_id=tenant.id, name=req.name, slug=req.slug, origin_url=req.origin_url, context=req.context)
    db.add(app)
    await db.commit()
    return {"id": str(app.id), "slug": app.slug, "name": app.name}


@router.post("/register")
async def register_tool(
    req: RegisterToolRequest,
    request: Request,
    tenant=Depends(resolve_tenant),
    db: AsyncSession = Depends(get_db),
):
    from app.models import App
    container = request.app.state.container
    result = await db.execute(
        select(App).where(App.tenant_id == tenant.id, App.slug == req.app_slug)
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")

    tool = await container.tool_registry.register(
        app_id=str(app.id),
        name=req.name,
        description=req.description,
        parameters=[
            {"name": k, "type": v.get("type", "string"), "description": v.get("description", ""), "required": k in req.tool_schema.get("required", [])}
            for k, v in req.tool_schema.get("properties", {}).items()
        ],
        endpoint=req.endpoint,
        method=req.method,
        headers=req.headers,
    )
    return {"id": tool.id, "name": tool.name}


@router.get("/list")
async def list_tools(
    request: Request,
    tenant=Depends(resolve_tenant),
    db: AsyncSession = Depends(get_db),
):
    from app.models import App
    container = request.app.state.container
    apps = await db.execute(select(App).where(App.tenant_id == tenant.id))
    all_tools = []
    for app in apps.scalars().all():
        tools = await container.tool_registry.list_by_app(str(app.id))
        all_tools.extend([
            {"id": t.id, "name": t.name, "description": t.description, "endpoint": t.endpoint, "method": t.method}
            for t in tools
        ])
    return {"tools": all_tools}


@router.post("/execute")
async def execute_tool(
    req: ExecuteToolRequest,
    request: Request,
    tenant=Depends(resolve_tenant),
):
    container = request.app.state.container
    result = await container.tool_registry.execute(
        tool_name=req.tool_name,
        app_id=req.app_id,
        args=req.arguments,
    )
    return result
