from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from fastapi.responses import StreamingResponse
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Tenant
from fastapi import Request

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    app_slug: Optional[str] = None


class ChatResponse(BaseModel):
    content: str
    conversation_id: str


async def resolve_tenant(
    request: Request,
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
    request.state.tenant = tenant
    return tenant


@router.post("/chat")
async def chat(
    req: ChatRequest,
    request: Request,
    tenant=Depends(resolve_tenant),
):
    container = request.app.state.container
    context_key = f"api:{tenant.id}"
    ctx = container.context_manager.get(context_key)
    if not ctx:
        ctx = container.context_manager.build(
            tenant_id=str(tenant.id),
            tenant_name=tenant.name,
            tenant_slug=tenant.slug,
            user_id="api-user",
            user_name="API User",
            user_email="api@kairos.local",
            app_slug=req.app_slug or "default",
        )
        container.context_manager.set(context_key, ctx)

    result = await container.orchestrator.process_message(
        message=req.message,
        context_key=context_key,
        conversation_id=req.conversation_id,
    )

    return ChatResponse(content=result["content"], conversation_id=result["conversation_id"])


@router.post("/chat/stream")
async def chat_stream(
    req: ChatRequest,
    request: Request,
    tenant=Depends(resolve_tenant),
):
    container = request.app.state.container
    context_key = f"api:{tenant.id}"

    async def generate():
        async for chunk in container.orchestrator.process_message_stream(
            message=req.message,
            context_key=context_key,
            conversation_id=req.conversation_id,
        ):
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")
