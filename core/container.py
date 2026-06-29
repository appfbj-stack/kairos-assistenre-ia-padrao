from core.application.orchestrator import Orchestrator
from core.application.context_manager import ContextManager
from core.application.memory_manager import MemoryManager
from core.application.tool_registry import ToolRegistry
from core.application.agent_manager import AgentManager
from core.application.prompt_composer import PromptComposer
from core.application.conversation_manager import ConversationManager
from core.application.event_bus import InMemoryEventBus
from core.application.audit_manager import AuditManager


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

        self.context_manager = ContextManager()
        self.conversation_manager = ConversationManager(self.conversation_repo) if conversation_repo else None
        self.memory_manager = MemoryManager(self.memory_repo, self.event_bus.publish) if memory_repo else None
        self.tool_registry = ToolRegistry(self.tool_repo, self.event_bus.publish) if tool_repo else None
        self.agent_manager = AgentManager(self.event_bus.publish)
        self.prompt_composer = PromptComposer()
        self.audit_manager = None
        self.orchestrator = None
        self.multimodal_engine = None

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
        return self
