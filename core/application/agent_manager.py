from typing import Optional
from core.domain.entities.agent import AgentDef, AgentCapability
from core.domain.entities.event import Event, EventType


class AgentManager:
    def __init__(self, publish_event: callable = None):
        self._agents: dict[str, AgentDef] = {}
        self._publish = publish_event

    def register(self, agent: AgentDef):
        self._agents[agent.name] = agent

    def get(self, name: str) -> Optional[AgentDef]:
        return self._agents.get(name)

    def list(self) -> list[AgentDef]:
        return list(self._agents.values())

    def find_for_intent(self, intent: str) -> Optional[AgentDef]:
        for agent in self._agents.values():
            if agent.is_active and agent.can_handle(intent):
                return agent
        return None

    async def execute(self, agent_name: str, input_data: dict) -> str:
        agent = self.get(agent_name)
        if not agent or not agent.executor:
            raise ValueError(f"Agent '{agent_name}' not found or has no executor")
        if self._publish:
            await self._publish(Event(EventType.AGENT_TRIGGERED, {"agent": agent_name, "input": input_data}))
        result = await agent.executor(input_data)
        if self._publish:
            await self._publish(Event(EventType.AGENT_COMPLETED, {"agent": agent_name, "result": result}))
        return result
