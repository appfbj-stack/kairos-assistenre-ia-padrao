from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel
from datetime import datetime, timezone
from kairos_aion_integration import CapabilityType

router = APIRouter(prefix="/api/aion", tags=["aion"])


class ExecuteRequest(BaseModel):
    name: str
    input_data: dict = {}


class ApproveRequest(BaseModel):
    approval_id: str
    decision: str
    decided_by: str = "system"


def _get_integration(request: Request):
    container = request.app.state.container
    if not container.aion_integration:
        raise HTTPException(status_code=503, detail="Aion integration not available")
    return container.aion_integration


@router.get("/status")
async def get_status(request: Request):
    integration = _get_integration(request)
    try:
        status = await integration.get_status()
        return {
            "connected": True,
            "initialized": True,
            "version": "0.1.0",
            "integrations": status,
        }
    except Exception:
        return {"connected": False, "initialized": False, "version": None}


@router.post("/initialize")
async def initialize(request: Request):
    integration = _get_integration(request)
    try:
        result = await integration.initialize()
        return {"status": "initialized", "connected": True, "details": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _skills_response(integration):
    return {"skills": [
        {
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "category": getattr(s, "category", "general"),
            "is_active": getattr(s, "is_active", True),
            "parameters": getattr(s, "parameters", []),
        }
        for s in integration.skills.list()
    ]}


@router.get("/skills")
async def list_skills(request: Request):
    return _skills_response(_get_integration(request))


@router.get("/mcps")
async def list_mcps(request: Request):
    integration = _get_integration(request)
    return {"mcps": [
        {
            "id": m.mcp.id,
            "name": m.mcp.name,
            "description": m.mcp.description,
            "endpoint": m.mcp.endpoint,
            "tools": m.get_tools(),
            "is_active": m.is_connected,
        }
        for m in integration.mcps.list()
    ]}


@router.get("/agents")
async def list_agents(request: Request):
    integration = _get_integration(request)
    caps = integration.discovery.get_by_type(CapabilityType.AGENT)
    return {"agents": [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "capabilities": c.parameters if isinstance(c.parameters, list) else [],
        }
        for c in caps
    ]}


@router.get("/capabilities")
async def list_capabilities(request: Request):
    integration = _get_integration(request)
    return {"capabilities": [
        {
            "name": c.name,
            "description": c.description,
            "type": c.type.value,
            "is_active": getattr(c, "is_active", True),
        }
        for c in integration.discovery.get_capabilities()
    ]}


@router.post("/execute")
async def execute(request: Request, body: ExecuteRequest):
    integration = _get_integration(request)
    audit_ctx = {"user_name": "api", "tenant_id": "default"}
    result = await integration.execute(body.name, body.input_data, audit_context=audit_ctx)
    return result


@router.post("/approve")
async def approve_action(request: Request, body: ApproveRequest):
    integration = _get_integration(request)
    if body.decision == "approve":
        req = integration.security.approve(body.approval_id, body.decided_by)
    elif body.decision == "reject":
        req = integration.security.reject(body.approval_id, body.decided_by)
    else:
        raise HTTPException(status_code=400, detail="Decision must be 'approve' or 'reject'")
    if not req:
        raise HTTPException(status_code=404, detail="Approval request not found or already decided")
    return {"status": req.status.value, "approval_id": req.id}


@router.get("/approvals/pending")
async def list_pending_approvals(request: Request):
    integration = _get_integration(request)
    approvals = integration.security.get_pending_approvals("*")
    return {"approvals": [
        {
            "id": a.id,
            "action": a.capability_name,
            "action_type": a.capability_type,
            "details": {"reason": "Ação requer aprovação"},
            "requested_by": a.requested_by,
            "created_at": a.created_at,
            "status": "pending",
        }
        for a in approvals
    ]}


@router.post("/skills/{skill_name}/toggle")
async def toggle_skill(request: Request, skill_name: str, active: bool = Query(True)):
    integration = _get_integration(request)
    if active:
        success = integration.skills.activate(skill_name)
    else:
        success = integration.skills.deactivate(skill_name)
    if not success:
        raise HTTPException(status_code=404, detail="Skill not found")
    skills_resp = _skills_response(integration)
    return {"status": "ok", "skill": skill_name, "active": active, "skills": skills_resp["skills"]}
