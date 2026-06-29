from __future__ import annotations
from typing import Optional, Callable

from .connector import AionConnector
from .discovery import AionDiscovery
from .skill_registry import AionSkillRegistry
from .mcp_manager import MCPManager
from .security import AionSecurity
from .models import AionCapability, CapabilityType, TaskResult


class AionIntegration:
    def __init__(
        self,
        connector: AionConnector,
        discovery: AionDiscovery,
        skill_registry: AionSkillRegistry,
        mcp_manager: MCPManager,
        security: AionSecurity,
        register_callback: Optional[Callable] = None,
        publish_event: Optional[Callable] = None,
    ):
        self.connector = connector
        self.discovery = discovery
        self.skills = skill_registry
        self.mcps = mcp_manager
        self.security = security
        self._register = register_callback
        self._publish = publish_event
        self._is_initialized = False

    async def initialize(self) -> dict:
        session = await self.connector.connect()

        capabilities = await self.discovery.discover_all()

        skills = [c for c in capabilities if c.type == CapabilityType.SKILL]
        from .models import AionSkill
        for s in skills:
            self.skills.register(AionSkill(
                id=s.id,
                name=s.name,
                description=s.description,
                parameters=s.parameters,
                is_active=s.is_active,
                category=s.metadata.get("category", "general"),
            ))

        mcps_list = [c for c in capabilities if c.type == CapabilityType.MCP]
        from .models import AionMCP
        for m in mcps_list:
            self.mcps.register(AionMCP(
                id=m.id,
                name=m.name,
                description=m.description,
                endpoint=m.metadata.get("endpoint", ""),
                tools=m.metadata.get("tools", []),
            ))

        if self._register:
            await self._register_capabilities(capabilities)

        self._is_initialized = True

        if self._publish:
            await self._publish({
                "type": "aion.initialized",
                "skills_count": len(skills),
                "mcps_count": len(mcps_list),
                "agents_count": len([c for c in capabilities if c.type == CapabilityType.AGENT]),
            })

        return {
            "status": "initialized",
            "session_id": session.id,
            "capabilities": {
                "skills": len(skills),
                "mcps": len(mcps_list),
                "agents": len([c for c in capabilities if c.type == CapabilityType.AGENT]),
            },
        }

    async def _register_capabilities(self, capabilities: list[AionCapability]):
        if not self._register:
            return
        for cap in capabilities:
            try:
                await self._register({
                    "name": f"aion_{cap.name}",
                    "description": f"[Aion {cap.type.value}] {cap.description}",
                    "type": cap.type.value,
                    "provider": "Aion",
                    "parameters": cap.parameters,
                    "is_active": cap.is_active,
                })
            except Exception:
                pass

    async def execute(self, name: str, input_data: dict, audit_context: Optional[dict] = None) -> dict:
        if not self._is_initialized:
            return {"error": "AionIntegration not initialized", "status": "error"}

        cap = self.discovery.get_by_name(name)
        if not cap:
            for skill in self.skills.list():
                if skill.name == name:
                    cap = AionCapability(
                        id=skill.id, name=skill.name, description=skill.description,
                        type=CapabilityType.SKILL, parameters=skill.parameters,
                    )
                    break

        if not cap:
            return {"error": f"Capability '{name}' not found in Aion", "status": "error"}

        if self.security.requires_approval(name):
            approval = self.security.request_approval(
                capability_name=name,
                capability_type=cap.type.value,
                input_data=input_data,
                requested_by=audit_context.get("user_name", "unknown") if audit_context else "unknown",
                tenant_id=audit_context.get("tenant_id", "") if audit_context else "",
            )
            return {
                "status": "approval_required",
                "approval_id": approval.id,
                "message": f"Ação '{name}' requer aprovação",
            }

        if cap.type == CapabilityType.SKILL:
            result = await self.connector.execute_skill(name, input_data)
        elif cap.type == CapabilityType.MCP:
            tool_name = input_data.pop("_tool", name)
            result = await self.connector.execute_mcp(name, tool_name, input_data)
        elif cap.type == CapabilityType.AGENT:
            result = await self.connector.execute_agent(name, input_data)
        else:
            result = TaskResult(success=False, error=f"Unknown capability type: {cap.type}")

        if self._publish:
            await self._publish({
                "type": "aion.executed",
                "capability": name,
                "success": result.success,
                "audit_context": audit_context or {},
            })

        if not result.success:
            return {"error": result.error, "status": "error"}

        return {"status": "ok", "data": result.data, "execution_time_ms": result.execution_time_ms}

    async def get_status(self) -> dict:
        aion_status = await self.connector.get_status()
        return {
            "connected": self.connector.is_connected,
            "initialized": self._is_initialized,
            "aion": aion_status,
            "skills_registered": self.skills.count(),
            "mcps_registered": len(self.mcps.list()),
            "pending_approvals": len(self.security.get_pending_approvals("*")),
        }

    def get_openai_tools(self) -> list[dict]:
        return self.skills.to_openai_tools() + self.mcps.to_openai_tools()

    async def find_and_execute(self, intent: str, input_data: dict, audit_context: Optional[dict] = None) -> dict:
        candidates = self.discovery.find_for_intent(intent)
        if not candidates:
            return {"status": "no_capability", "message": "Nenhuma capacidade Aion encontrada para esta intenção"}

        best = candidates[0]
        return await self.execute(best.name, input_data, audit_context)
