from __future__ import annotations
import httpx
import uuid
from datetime import datetime, timedelta
from typing import Any, Optional

from .models import (
    AionSession,
    AionTask,
    AionCapability,
    AionSkill,
    AionMCP,
    AionAgent,
    CapabilityType,
    ExecutionStatus,
    TaskResult,
)


class AionConnector:
    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        api_key: str = "",
        timeout: int = 60,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._session: Optional[AionSession] = None
        self._http: Optional[httpx.AsyncClient] = None

    @property
    def is_connected(self) -> bool:
        return self._session is not None and self._session.is_valid

    async def connect(self) -> AionSession:
        self._http = httpx.AsyncClient(timeout=self.timeout)
        if self.api_key:
            self._http.headers["Authorization"] = f"Bearer {self.api_key}"
        self._session = AionSession(
            id=str(uuid.uuid4()),
            token=self.api_key or str(uuid.uuid4()),
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
        return self._session

    async def disconnect(self):
        if self._http:
            await self._http.aclose()
        self._session = None

    async def _request(
        self,
        method: str,
        path: str,
        json_data: dict | None = None,
    ) -> dict:
        if not self._http:
            raise RuntimeError("AionConnector not connected. Call connect() first.")
        url = f"{self.base_url}{path}"
        try:
            response = await self._http.request(method, url, json=json_data)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            return {"error": "timeout", "message": f"Request to {url} timed out"}
        except httpx.HTTPStatusError as e:
            return {
                "error": "http_error",
                "message": str(e),
                "status_code": e.response.status_code,
            }
        except Exception as e:
            return {"error": "unknown", "message": str(e)}

    async def list_skills(self) -> list[AionSkill]:
        result = await self._request("GET", "/api/aion/skills")
        if "error" in result:
            return self._demo_skills()
        return [AionSkill(**s) for s in result.get("skills", [])]

    async def list_mcps(self) -> list[AionMCP]:
        result = await self._request("GET", "/api/aion/mcps")
        if "error" in result:
            return self._demo_mcps()
        return [AionMCP(**m) for m in result.get("mcps", [])]

    async def list_agents(self) -> list[AionAgent]:
        result = await self._request("GET", "/api/aion/agents")
        if "error" in result:
            return self._demo_agents()
        return [AionAgent(**a) for a in result.get("agents", [])]

    async def execute_skill(self, skill_name: str, params: dict) -> TaskResult:
        result = await self._request(
            "POST",
            "/api/aion/execute",
            json_data={"type": "skill", "name": skill_name, "params": params},
        )
        if "error" in result:
            return TaskResult(success=False, error=result["message"])
        return TaskResult(
            success=True,
            data=result.get("data"),
            execution_time_ms=result.get("execution_time_ms"),
        )

    async def execute_mcp(self, mcp_name: str, tool_name: str, params: dict) -> TaskResult:
        result = await self._request(
            "POST",
            "/api/aion/mcp/execute",
            json_data={
                "mcp_name": mcp_name,
                "tool_name": tool_name,
                "params": params,
            },
        )
        if "error" in result:
            return TaskResult(success=False, error=result["message"])
        return TaskResult(
            success=True,
            data=result.get("data"),
            execution_time_ms=result.get("execution_time_ms"),
        )

    async def execute_agent(self, agent_name: str, input_data: dict) -> TaskResult:
        result = await self._request(
            "POST",
            "/api/aion/agent/execute",
            json_data={"agent_name": agent_name, "input": input_data},
        )
        if "error" in result:
            return TaskResult(success=False, error=result["message"])
        return TaskResult(
            success=True,
            data=result.get("data"),
            execution_time_ms=result.get("execution_time_ms"),
        )

    async def get_status(self) -> dict:
        result = await self._request("GET", "/api/aion/status")
        if "error" in result:
            return {"status": "unavailable", "error": result["message"]}
        return {
            "status": result.get("status", "unknown"),
            "skills_count": result.get("skills_count", 0),
            "mcps_count": result.get("mcps_count", 0),
            "agents_count": result.get("agents_count", 0),
            "uptime": result.get("uptime", 0),
        }

    def _demo_skills(self) -> list[AionSkill]:
        return [
            AionSkill(
                id="skill-doc-001",
                name="analisar_documento",
                description="Analisa contratos, PDFs e documentos extraindo informações estruturadas",
                parameters=[
                    {"name": "documento", "type": "string", "description": "Texto ou URL do documento", "required": True},
                    {"name": "tipo_analise", "type": "string", "description": "Tipo: resumo, extrair_dados, revisar_clausulas"},
                ],
                category="documentos",
            ),
            AionSkill(
                id="skill-report-001",
                name="gerar_relatorio",
                description="Gera relatórios estruturados a partir de dados brutos",
                parameters=[
                    {"name": "dados", "type": "string", "description": "Dados para o relatório", "required": True},
                    {"name": "formato", "type": "string", "description": "Formato: pdf, csv, json"},
                    {"name": "template", "type": "string", "description": "Template opcional"},
                ],
                category="relatorios",
            ),
            AionSkill(
                id="skill-data-001",
                name="analisar_dados",
                description="Analisa dados, identifica padrões e gera insights",
                parameters=[
                    {"name": "dados", "type": "string", "description": "Dados para análise", "required": True},
                    {"name": "tipo_analise", "type": "string", "description": "Tipo: tendencias, agrupamento, correlacao"},
                ],
                category="dados",
            ),
        ]

    def _demo_mcps(self) -> list[AionMCP]:
        return [
            AionMCP(
                id="mcp-email-001",
                name="MCP Email",
                description="Envio e gerenciamento de e-mails",
                endpoint="/api/aion/mcp/email",
                auth_type="none",
                tools=[
                    {"name": "enviar_email", "description": "Envia e-mail", "parameters": {"para": "string", "assunto": "string", "corpo": "string"}},
                    {"name": "listar_emails", "description": "Lista e-mails da caixa de entrada"},
                ],
            ),
            AionMCP(
                id="mcp-file-001",
                name="MCP Arquivos",
                description="Leitura e gerenciamento de arquivos",
                endpoint="/api/aion/mcp/files",
                auth_type="none",
                tools=[
                    {"name": "ler_arquivo", "description": "Lê conteúdo de arquivo", "parameters": {"caminho": "string"}},
                    {"name": "salvar_arquivo", "description": "Salva conteúdo em arquivo", "parameters": {"caminho": "string", "conteudo": "string"}},
                ],
            ),
            AionMCP(
                id="mcp-calendar-001",
                name="MCP Calendário",
                description="Gerenciamento de eventos e calendário",
                endpoint="/api/aion/mcp/calendar",
                auth_type="none",
                tools=[
                    {"name": "criar_evento", "description": "Cria evento no calendário", "parameters": {"titulo": "string", "data": "string", "descricao": "string"}},
                ],
            ),
        ]

    def _demo_agents(self) -> list[AionAgent]:
        return [
            AionAgent(
                id="agent-fin-001",
                name="Agente Financeiro",
                description="Analisa finanças, gera relatórios financeiros e recomenda ações",
                capabilities=["financeiro", "finance", "receita", "despesa", "faturamento", "fluxo de caixa"],
                type="finance",
            ),
            AionAgent(
                id="agent-doc-001",
                name="Agente Documentos",
                description="Processa, analisa e organiza documentos",
                capabilities=["documento", "contrato", "pdf", "arquivo", "documentação"],
                type="documentos",
            ),
            AionAgent(
                id="agent-dev-001",
                name="Agente Desenvolvimento",
                description="Auxilia em tarefas de desenvolvimento, revisão de código e arquitetura",
                capabilities=["desenvolvimento", "código", "code", "programação", "bug", "feature"],
                type="development",
            ),
            AionAgent(
                id="agent-support-001",
                name="Agente Atendimento",
                description="Atende usuários, responde perguntas e resolve problemas",
                capabilities=["atendimento", "suporte", "ajuda", "dúvida", "problema"],
                type="support",
            ),
        ]
