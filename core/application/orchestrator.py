import json
import uuid
from typing import Optional, AsyncGenerator

from core.domain.entities.context import RuntimeContext
from core.domain.entities.conversation import MessageRole
from core.domain.entities.event import Event, EventType
from core.domain.interfaces.llm_port import LLMPort
from core.domain.interfaces.conversation_port import ConversationPort

from core.application.conversation_manager import ConversationManager
from core.application.context_manager import ContextManager
from core.application.memory_manager import MemoryManager
from core.application.tool_registry import ToolRegistry
from core.application.agent_manager import AgentManager
from core.application.prompt_composer import PromptComposer
from core.application.event_bus import InMemoryEventBus


class Orchestrator:
    def __init__(
        self,
        context_manager: ContextManager,
        conversation_manager: ConversationManager,
        memory_manager: MemoryManager,
        tool_registry: ToolRegistry,
        agent_manager: AgentManager,
        prompt_composer: PromptComposer,
        event_bus: InMemoryEventBus,
        llm: LLMPort,
    ):
        self.context = context_manager
        self.conversations = conversation_manager
        self.memory = memory_manager
        self.tools = tool_registry
        self.agents = agent_manager
        self.prompts = prompt_composer
        self.events = event_bus
        self.llm = llm
        self._default_model = "openrouter/auto"

    async def process_message(
        self,
        message: str,
        context_key: str,
        conversation_id: Optional[str] = None,
    ) -> dict:
        ctx = self.context.get(context_key)
        if not ctx:
            raise ValueError(f"Context not found: {context_key}")

        await self.events.publish(Event(EventType.CONVERSATION_STARTED, {
            "context_key": context_key, "message": message[:100]
        }))

        if not conversation_id:
            conv = await self.conversations.create(ctx.tenant.id, ctx.app.id, ctx.user.id)
            conversation_id = conv.id

        await self.conversations.add_user_message(conversation_id, message)
        await self.events.publish(Event(EventType.MESSAGE_SENT, {
            "conversation_id": conversation_id, "message": message[:100]
        }))

        history = await self.conversations.get_history(conversation_id)
        llm_history = [{"role": m.role.value, "content": m.content} for m in history]

        app_tools = await self.tools.list_by_app(ctx.app.id) if ctx.app.id else []
        openai_tools = self.tools.to_openai_tools(app_tools)

        agent = self.agents.find_for_intent(message)
        if agent:
            await self.events.publish(Event(EventType.AGENT_TRIGGERED, {"agent": agent.name}))

        system_prompt = self.prompts.compose(context=ctx)

        await self.events.publish(Event(EventType.LLM_CALLED, {
            "conversation_id": conversation_id, "tools_count": len(openai_tools)
        }))

        response = await self.llm.chat(
            messages=[{"role": "system", "content": system_prompt}] + llm_history,
            model=ctx.tenant.slug,
            tools=openai_tools if openai_tools else None,
        )

        choice = response["choices"][0]
        msg = choice["message"]
        final_content = msg.get("content") or ""

        if msg.get("tool_calls"):
            audit_ctx = {
                "tenant_id": ctx.tenant.id,
                "user_id": ctx.user.id,
                "user_name": ctx.user.name,
                "user_role": ctx.user.role.value,
                "app_slug": ctx.app.slug,
            }
            for tc in msg["tool_calls"]:
                fn = tc["function"]
                try:
                    args = json.loads(fn["arguments"])
                    result = await self.tools.execute(fn["name"], ctx.app.id, args, audit_context=audit_ctx)
                    final_content += f"\n\n[Ferramenta '{fn['name']}' executada]"
                except ValueError:
                    final_content += f"\n\n[Ferramenta '{fn['name']}' não encontrada]"

        await self.conversations.add_assistant_message(conversation_id, final_content)
        await self.events.publish(Event(EventType.MESSAGE_RECEIVED, {
            "conversation_id": conversation_id, "content_length": len(final_content)
        }))

        return {
            "conversation_id": conversation_id,
            "content": final_content,
        }

    async def process_message_stream(
        self,
        message: str,
        context_key: str,
        conversation_id: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        ctx = self.context.get(context_key)
        if not ctx:
            raise ValueError(f"Context not found: {context_key}")

        if not conversation_id:
            conv = await self.conversations.create(ctx.tenant.id, ctx.app.id, ctx.user.id)
            conversation_id = conv.id

        await self.conversations.add_user_message(conversation_id, message)

        history = await self.conversations.get_history(conversation_id)
        llm_history = [{"role": m.role.value, "content": m.content} for m in history]

        app_tools = await self.tools.list_by_app(ctx.app.id) if ctx.app.id else []
        openai_tools = self.tools.to_openai_tools(app_tools)

        system_prompt = self.prompts.compose(context=ctx)

        full_response = ""
        async for chunk in self.llm.chat_stream(
            messages=[{"role": "system", "content": system_prompt}] + llm_history,
            model=ctx.tenant.slug,
            tools=openai_tools if openai_tools else None,
        ):
            full_response += chunk
            yield chunk

        await self.conversations.add_assistant_message(conversation_id, full_response)
