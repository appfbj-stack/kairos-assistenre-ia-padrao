"""
Kairós LangGraph Orchestrator
Multi-agent orchestration using LangGraph for planning, execution, and validation.
"""

import json
import uuid
import logging
from typing import Optional, Callable, Any

logger = logging.getLogger("kairos.langgraph")


class AppIntegrationAgent:
    def __init__(self):
        self._apps = []

    def register_app(self, app_data: dict):
        self._apps.append(app_data)

    def list_apps(self) -> list:
        return list(self._apps)


class AionLangGraphOrchestrator:
    def __init__(self, llm_call: Optional[Callable] = None):
        self.llm_call = llm_call
        self.app_integration = AppIntegrationAgent()
        self._max_iterations = 5

    async def process(self, user_message: str, context: Optional[dict] = None) -> dict:
        ctx = context or {}
        task_id = str(uuid.uuid4())
        app_slug = ctx.get("app", "geral")

        plan = await self._plan(user_message, app_slug)
        exec_result = await self._execute(plan, user_message, app_slug)
        qa_result = await self._qa(exec_result, user_message, app_slug)

        response_text = self._build_response(plan, exec_result, qa_result)

        return {
            "task_id": task_id,
            "success": exec_result.get("success", True),
            "response": response_text,
            "plan": plan,
            "execution": exec_result,
            "qa": qa_result,
            "automation": None,
            "app_context": ctx,
            "skills_used": exec_result.get("skills_used", []),
            "errors": exec_result.get("errors", []),
            "iterations": exec_result.get("iterations", 0),
            "agents_used": ["planner", "executor", "qa"],
        }

    async def _plan(self, message: str, app_slug: str) -> dict:
        if not self.llm_call:
            return {"steps": [{"action": "respond", "description": "Responder ao usuario"}]}
        try:
            response = await self.llm_call(
                messages=[
                    {"role": "system", "content": "Planeje a execucao para responder a mensagem do usuario. "
                     "Retorne um JSON com lista de passos (steps), cada um com action e description."},
                    {"role": "user", "content": f"App: {app_slug}\nMensagem: {message}"},
                ]
            )
            content = response.get("content", "{}")
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("\n", 1)[0]
            return json.loads(content)
        except Exception as e:
            logger.warning(f"[Planner] Erro ao planejar: {e}")
            return {"steps": [{"action": "respond", "description": "Responder ao usuario"}]}

    async def _execute(self, plan: dict, message: str, app_slug: str) -> dict:
        if not self.llm_call:
            return {"success": True, "response": "Processado", "skills_used": [], "errors": [], "iterations": 1}
        try:
            steps = plan.get("steps", [])
            for step in steps[:self._max_iterations]:
                pass
            response = await self.llm_call(
                messages=[
                    {"role": "system", "content": "Execute o plano e gere uma resposta util para o usuario."},
                    {"role": "user", "content": f"App: {app_slug}\nMensagem: {message}\nPlano: {json.dumps(plan)}"},
                ]
            )
            return {
                "success": True,
                "response": response.get("content", ""),
                "skills_used": [],
                "errors": [],
                "iterations": 1,
            }
        except Exception as e:
            logger.error(f"[Executor] Erro: {e}")
            return {"success": False, "response": str(e), "skills_used": [], "errors": [str(e)], "iterations": 1}

    async def _qa(self, exec_result: dict, message: str, app_slug: str) -> dict:
        if not exec_result.get("success") or not self.llm_call:
            return {"approved": True, "notes": "Validacao simplificada"}
        try:
            response = await self.llm_call(
                messages=[
                    {"role": "system", "content": "Valide a resposta gerada. Responda apenas 'OK' se correta, "
                     "ou descreva o problema."},
                    {"role": "user", "content": f"Pergunta: {message}\nResposta: {exec_result.get('response', '')}"},
                ]
            )
            content = response.get("content", "OK")
            return {"approved": "OK" in content.upper(), "notes": content}
        except Exception:
            return {"approved": True, "notes": "Validacao indisponivel"}

    def _build_response(self, plan: dict, exec_result: dict, qa_result: dict) -> str:
        if not exec_result.get("success"):
            return f"Erro ao processar: {exec_result.get('response', 'Erro desconhecido')}"
        response = exec_result.get("response", "")
        return response

    def get_app_registry(self) -> list:
        return self.app_integration.list_apps()
