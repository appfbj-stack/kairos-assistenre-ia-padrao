from core.application.orchestrator import Orchestrator
from core.application.context_manager import ContextManager
from core.application.memory_manager import MemoryManager
from core.application.tool_registry import ToolRegistry
from core.application.agent_manager import AgentManager
from core.application.prompt_composer import PromptComposer
from core.application.conversation_manager import ConversationManager
from core.application.event_bus import InMemoryEventBus
from core.application.audit_manager import AuditManager
from kairos_aion_integration import AionIntegration, AionConnector, AionDiscovery, AionSkillRegistry, MCPManager, AionSecurity


class Container:
    def __init__(
        self,
        conversation_repo=None,
        memory_repo=None,
        tool_repo=None,
        audit_repo=None,
        llm=None,
        openrouter_key="",
        tts_key="",
        voice_provider="openai",
        aion_base_url="",
        aion_api_key="",
    ):
        self.event_bus = InMemoryEventBus()
        self.conversation_repo = conversation_repo
        self.memory_repo = memory_repo
        self.tool_repo = tool_repo
        self.audit_repo = audit_repo
        self.llm = llm
        self.openrouter_key = openrouter_key
        self.tts_key = tts_key
        self.voice_provider = voice_provider
        self.aion_base_url = aion_base_url
        self.aion_api_key = aion_api_key

        self.context_manager = ContextManager()
        self.conversation_manager = ConversationManager(self.conversation_repo) if conversation_repo else None
        self.memory_manager = MemoryManager(self.memory_repo, self.event_bus.publish) if memory_repo else None
        self.tool_registry = ToolRegistry(self.tool_repo, self.event_bus.publish) if tool_repo else None
        self.agent_manager = AgentManager(self.event_bus.publish)
        self.prompt_composer = PromptComposer()
        self.audit_manager = None
        self.orchestrator = None
        self.multimodal_engine = None
        self.aion_integration = None

    def build(self):
        if self.audit_repo:
            self.audit_manager = AuditManager(self.audit_repo, self.event_bus)
        if all([self.conversation_repo, self.llm]):
            self.orchestrator = Orchestrator(
                context_manager=self.context_manager,
                conversation_manager=self.conversation_manager,
                memory_manager=self.memory_manager,
                tool_registry=self.tool_registry,
                agent_manager=self.agent_manager,
                prompt_composer=self.prompt_composer,
                event_bus=self.event_bus,
                llm=self.llm,
                aion_integration=self.aion_integration,
            )
        try:
            from app.multimodal.engine import MultimodalEngine
            self.multimodal_engine = MultimodalEngine(
                openrouter_key=self.openrouter_key,
                voice_tts_key=self.tts_key,
                voice_provider=self.voice_provider,
            )
        except Exception:
            pass

        self.aion_integration = self._build_aion()
        return self

    def _build_aion(self):
        try:
            connector = AionConnector(
                base_url=self.aion_base_url or "http://localhost:8080",
                api_key=self.aion_api_key,
            )
            discovery = AionDiscovery(connector)
            skill_registry = AionSkillRegistry()
            mcp_manager = MCPManager()
            security = AionSecurity()
            return AionIntegration(
                connector=connector,
                discovery=discovery,
                skill_registry=skill_registry,
                mcp_manager=mcp_manager,
                security=security,
                register_callback=self._register_aion_capability,
                publish_event=self.event_bus.publish if hasattr(self.event_bus, "publish") else None,
            )
        except Exception:
            return None

    async def _register_aion_capability(self, capability: dict):
        if not self.tool_registry or not self.context_manager:
            return
        pass
