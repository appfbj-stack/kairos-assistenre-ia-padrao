from fastapi import APIRouter, Depends, HTTPException, Header, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Tenant
import json
import logging

logger = logging.getLogger("kairos.agent")

router = APIRouter(prefix="/api/agent", tags=["agent"])

active_agents: dict = {}


class AgentConnection:
    def __init__(self, ws: WebSocket, tenant_id: str, device_id: str, device_name: str):
        self.ws = ws
        self.tenant_id = tenant_id
        self.device_id = device_id
        self.device_name = device_name


@router.websocket("/ws")
async def agent_websocket(
    websocket: WebSocket,
    token: str = Query(""),
    db: AsyncSession = Depends(get_db),
):
    await websocket.accept()
    agent = None
    try:
        api_key = token

        result = await db.execute(
            select(Tenant).where(Tenant.api_key == api_key, Tenant.is_active == True)
        )
        tenant = result.scalar_one_or_none()
        if not tenant:
            await websocket.send_text(json.dumps({
                "type": "auth_response",
                "payload": {"status": "error", "message": "Invalid API key"},
                "message_id": "0",
            }))
            await websocket.close()
            return

        auth_ok = json.dumps({
            "type": "auth_response",
            "payload": {"status": "ok", "tenant_id": str(tenant.id)},
            "message_id": "0",
        })
        await websocket.send_text(auth_ok)

        agent = AgentConnection(websocket, str(tenant.id), "", f"Agent-{tenant.slug}")
        active_agents[str(tenant.id)] = agent
        logger.info(f"Agent connected: tenant={tenant.slug}")

        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            msg_type = data.get("type", "")

            if msg_type == "auth_request":
                payload = data.get("payload", {})
                if agent:
                    agent.device_id = payload.get("device_id", agent.device_id)
                    agent.device_name = payload.get("device_name", agent.device_name)
                await websocket.send_text(json.dumps({
                    "type": "auth_response",
                    "payload": {"status": "ok", "device_id": agent.device_id if agent else ""},
                    "message_id": data.get("message_id", ""),
                }))
                logger.info(f"Agent authenticated: {agent.device_name if agent else 'unknown'}")

            elif msg_type == "task_result":
                logger.info(f"Task result: {data.get('payload', {})}")

            elif msg_type == "agent_log":
                logger.info(f"Agent log: {data.get('payload', {})}")

            elif msg_type == "pong":
                pass

            elif msg_type == "status_update":
                pass

    except WebSocketDisconnect:
        if agent:
            active_agents.pop(agent.tenant_id, None)
            logger.info(f"Agent disconnected: {agent.device_id or agent.tenant_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if agent:
            active_agents.pop(agent.tenant_id, None)


@router.post("/command")
async def send_command(
    tenant_id: str,
    command_type: str,
    params: dict = {},
    authorization: str = Header(None),
):
    agent = active_agents.get(tenant_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not connected")

    import uuid, time
    msg = json.dumps({
        "type": "task_assign",
        "payload": {"type": command_type, "params": params},
        "message_id": uuid.uuid4().hex[:12],
        "timestamp": time.time(),
        "device_id": agent.device_id,
    })
    await agent.ws.send_text(msg)
    return {"sent": True, "message_id": uuid.uuid4().hex[:12]}


@router.get("/status/{tenant_id}")
async def agent_status(tenant_id: str):
    agent = active_agents.get(tenant_id)
    if agent:
        return {"connected": True, "device_id": agent.device_id, "device_name": agent.device_name}
    return {"connected": False}
