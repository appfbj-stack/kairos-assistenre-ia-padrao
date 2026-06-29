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
        aion_integration=None,
    ):
        self.context = context_manager
        self.conversations = conversation_manager
        self.memory = memory_manager
        self.tools = tool_registry
        self.agents = agent_manager
        self.prompts = prompt_composer
        self.events = event_bus
        self.llm = llm
        self.aion = aion_integration
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

        aion_tools = []
        if self.aion and self.aion._is_initialized:
            aion_tools = self.aion.get_openai_tools()
            openai_tools.extend(aion_tools)

        agent = self.agents.find_for_intent(message)
        if agent:
            await self.events.publish(Event(EventType.AGENT_TRIGGERED, {"agent": agent.name}))

        aion_candidates = []
        if self.aion and self.aion._is_initialized:
            aion_candidates = self.aion.discovery.find_for_intent(message)

        system_prompt = self.prompts.compose(context=ctx)
        system_prompt += "\n\nVocê tem acesso a capacidades do Aion (Skills, MCPs, Agentes especializados)."
        system_prompt += "\nSkills Aion têm o prefixo 'aion_', MCPs têm o prefixo 'mcp_'."
        system_prompt += "\nUse a ferramenta mais adequada para cada tarefa."

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
                    tool_name = fn["name"]
                    if tool_name.startswith("aion_") and self.aion:
                        skill_name = tool_name.replace("aion_", "")
                        result_data = await self.aion.execute(skill_name, args, audit_context=audit_ctx)
                        status = result_data.get("status", "error")
                        if status == "approval_required":
                            final_content += f"\n\n[Ação '{tool_name}' requer aprovação - ID: {result_data.get('approval_id')}]"
                        elif status == "ok":
                            final_content += f"\n\n[Aion Skill '{skill_name}' executada]"
                        else:
                            final_content += f"\n\n[Erro Aion: {result_data.get('error', 'desconhecido')}]"
                    elif tool_name.startswith("mcp_") and self.aion:
                        parts = tool_name.split("_", 2)
                        if len(parts) == 3:
                            _, mcp_name, mcp_tool = parts
                            result_data = await self.aion.execute(mcp_name, {"_tool": mcp_tool, **args}, audit_context=audit_ctx)
                            status = result_data.get("status", "error")
                            if status == "ok":
                                final_content += f"\n\n[MCP '{mcp_name}/{mcp_tool}' executado]"
                            else:
                                final_content += f"\n\n[Erro MCP: {result_data.get('error', 'desconhecido')}]"
                        else:
                            final_content += f"\n\n[MCP '{tool_name}' formato inválido]"
                    else:
                        result = await self.tools.execute(tool_name, ctx.app.id, args, audit_context=audit_ctx)
                        final_content += f"\n\n[Ferramenta '{tool_name}' executada]"
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

        if self.aion and self.aion._is_initialized:
            openai_tools.extend(self.aion.get_openai_tools())

        system_prompt = self.prompts.compose(context=ctx)
        system_prompt += "\n\nVocê tem acesso a capacidades do Aion (Skills, MCPs, Agentes especializados)."
        system_prompt += "\nSkills Aion têm o prefixo 'aion_', MCPs têm o prefixo 'mcp_'."

        full_response = ""
        async for chunk in self.llm.chat_stream(
            messages=[{"role": "system", "content": system_prompt}] + llm_history,
            model=ctx.tenant.slug,
            tools=openai_tools if openai_tools else None,
        ):
            full_response += chunk
            yield chunk

        await self.conversations.add_assistant_message(conversation_id, full_response)
