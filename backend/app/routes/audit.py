from fastapi import APIRouter, Depends, HTTPException, Header, Query
from fastapi import Request as Req
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Tenant

router = APIRouter(prefix="/api/audit", tags=["audit"])


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


@router.get("/logs")
async def get_audit_logs(
    request: Req,
    event_type: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    tool_name: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0),
    tenant=Depends(resolve_tenant),
):
    audit = request.app.state.container.audit_manager
    logs = await audit.query(
        tenant_id=str(tenant.id),
        event_type=event_type,
        user_id=user_id,
        tool_name=tool_name,
        limit=limit,
        offset=offset,
    )
    total = await audit.count(
        tenant_id=str(tenant.id),
        event_type=event_type,
        user_id=user_id,
    )
    return {"total": total, "limit": limit, "offset": offset, "logs": [
        {
            "id": log.id,
            "event_type": log.event_type,
            "tool_name": log.tool_name,
            "app_slug": log.app_slug,
            "user_id": log.user_id,
            "user_name": log.user_name,
            "user_role": log.user_role,
            "input_data": log.input_data,
            "result": log.result,
            "success": log.success,
            "created_at": log.created_at,
        }
        for log in logs
    ]}


class RecordAuditRequest(BaseModel):
    event_type: str
    tool_name: Optional[str] = None
    input_data: Optional[str] = None
    result: Optional[str] = None
    success: bool = True


@router.post("/record")
async def record_audit(
    req: RecordAuditRequest,
    request: Req,
    tenant=Depends(resolve_tenant),
):
    audit = request.app.state.container.audit_manager
    entry = await audit.record(
        tenant_id=str(tenant.id),
        event_type=req.event_type,
        tool_name=req.tool_name,
        input_data=req.input_data,
        result=req.result,
        success=req.success,
    )
    return {"id": entry.id, "event_type": entry.event_type}
