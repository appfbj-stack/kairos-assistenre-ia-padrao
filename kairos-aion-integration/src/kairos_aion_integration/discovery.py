from __future__ import annotations
from typing import Optional

from .connector import AionConnector
from .models import AionCapability, CapabilityType, AionSkill, AionMCP, AionAgent


class AionDiscovery:
    def __init__(self, connector: AionConnector):
        self._connector = connector
        self._capabilities: list[AionCapability] = []

    async def discover_all(self) -> list[AionCapability]:
        capabilities: list[AionCapability] = []

        skills = await self._connector.list_skills()
        for s in skills:
            capabilities.append(
                AionCapability(
                    id=s.id,
                    name=s.name,
                    description=s.description,
                    type=CapabilityType.SKILL,
                    parameters=s.parameters,
                    is_active=s.is_active,
                    metadata={"source": s.source, "category": s.category},
                )
            )

        mcps = await self._connector.list_mcps()
        for m in mcps:
            capabilities.append(
                AionCapability(
                    id=m.id,
                    name=m.name,
                    description=m.description,
                    type=CapabilityType.MCP,
                    is_active=m.is_active,
                    metadata={"endpoint": m.endpoint, "tools": m.tools},
                )
            )

        agents = await self._connector.list_agents()
        for a in agents:
            capabilities.append(
                AionCapability(
                    id=a.id,
                    name=a.name,
                    description=a.description,
                    type=CapabilityType.AGENT,
                    is_active=a.is_active,
                    metadata={"capabilities": a.capabilities, "model": a.model},
                )
            )

        self._capabilities = capabilities
        return capabilities

    def get_capabilities(self) -> list[AionCapability]:
        return self._capabilities

    def get_by_type(self, cap_type: CapabilityType) -> list[AionCapability]:
        return [c for c in self._capabilities if c.type == cap_type]

    def get_by_name(self, name: str) -> Optional[AionCapability]:
        for c in self._capabilities:
            if c.name == name:
                return c
        return None

    def find_for_intent(self, intent: str) -> list[AionCapability]:
        intent_lower = intent.lower()
        scored: list[tuple[AionCapability, int]] = []
        for cap in self._capabilities:
            score = 0
            words = cap.name.lower().split("_")
            for w in words:
                if w in intent_lower:
                    score += 2
            desc_words = cap.description.lower().split()
            for w in desc_words:
                if len(w) > 3 and w in intent_lower:
                    score += 1
            for p in cap.parameters:
                if p.get("name", "").lower() in intent_lower:
                    score += 1
            if cap.metadata.get("category", "").lower() in intent_lower:
                score += 2
            if isinstance(cap.metadata.get("capabilities"), list):
                for c in cap.metadata["capabilities"]:
                    if c.lower() in intent_lower:
                        score += 3
            if score > 0:
                scored.append((cap, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in scored]
