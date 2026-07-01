from fastapi import APIRouter, HTTPException, Request, Depends, Query
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.agents.langgraph_orchestrator import AionLangGraphOrchestrator
from app.agents.church.church_agent import AionChurchAgent

router = APIRouter(prefix="/api/agents", tags=["agents-langgraph"])

# Instancias compartilhadas
_church_agent = AionChurchAgent()


class AgentMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    app: Optional[str] = "geral"
    context: Optional[dict] = None


class ChurchMessage(BaseModel):
    message: str
    session_id: str


async def _get_llm_call(request: Request):
    """Retorna funcao de chamada LLM do container."""
    container = getattr(request.app.state, "container", None)
    if not container or not container.llm:
        return None

    async def llm_call(messages: list, model: str = None, tools=None) -> dict:
        try:
            response = await container.llm.chat(
                messages=messages,
                model=model or "openrouter/auto",
                tools=tools,
            )
            choice = response.get("choices", [{}])[0]
            msg = choice.get("message", {})
            return {"content": msg.get("content", ""), "tool_calls": msg.get("tool_calls")}
        except Exception as e:
            return {"content": f"Erro LLM: {str(e)}", "tool_calls": None}

    return llm_call


@router.post("/process")
async def process_with_agents(
    body: AgentMessage,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Processa mensagem pelo sistema multi-agente LangGraph."""
    llm_call = await _get_llm_call(request)

    if not llm_call:
        return {
            "task_id": "no-llm",
            "response": "LLM nao configurado. Configure OPENROUTER_API_KEY.",
            "success": False,
        }

    orchestrator = AionLangGraphOrchestrator(llm_call=llm_call)
    context = body.context or {}
    context["app"] = body.app or "geral"

    result = await orchestrator.process(
        user_message=body.message,
        context=context,
    )
    return result


@router.post("/church/chat")
async def church_chat(
    body: ChurchMessage,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Endpoint do Church Agent - cadastro conversacional de membros."""
    agent = AionChurchAgent(db_session=db)
    result = await agent.handle_message(
        message=body.message,
        session_id=body.session_id,
    )
    return result


@router.get("/church/members")
async def church_list_members(
    congregacao: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Lista membros via Church Agent."""
    agent = AionChurchAgent(db_session=db)
    return await agent.list_members(congregacao=congregacao)


@router.get("/church/members/search")
async def church_search_members(
    q: str = Query(..., min_length=2),
    db: AsyncSession = Depends(get_db),
):
    """Busca membros via Church Agent."""
    agent = AionChurchAgent(db_session=db)
    return await agent.search_members(q)


@router.get("/apps")
async def list_registered_apps(request: Request):
    """Lista todos os aplicativos registrados no App Integration Agent."""
    from app.agents.langgraph_orchestrator import AppIntegrationAgent
    agent = AppIntegrationAgent()
    return {"apps": agent.list_apps()}


@router.get("/skills")
async def list_available_skills(db: AsyncSession = Depends(get_db)):
    """Lista Skills aprovadas na biblioteca."""
    try:
        from sqlalchemy import select
        from app.models.skill import Skill
        result = await db.execute(
            select(Skill).where(Skill.aprovada == True, Skill.ativa == True)
        )
        skills = result.scalars().all()
        return {
            "skills": [
                {
                    "id": s.id,
                    "nome": s.nome,
                    "versao": s.versao,
                    "descricao": s.descricao,
                    "categoria": s.categoria,
                    "agente_criador": s.agente_criador,
                    "uso_count": s.uso_count,
                }
                for s in skills
            ],
            "total": len(skills),
        }
    except Exception as e:
        return {"skills": [], "total": 0, "error": str(e)}


@router.get("/status")
async def agents_status():
    """Status do sistema de agentes."""
    try:
        from langgraph.graph import StateGraph
        langgraph_ok = True
    except ImportError:
        langgraph_ok = False

    return {
        "status": "operational",
        "langgraph_available": langgraph_ok,
        "agents": [
            {"name": "planner", "status": "active", "description": "Arquiteto - analisa e planeja"},
            {"name": "executor", "status": "active", "description": "Construtor - executa acoes"},
            {"name": "qa", "status": "active", "description": "Validador - testa e aprova"},
            {"name": "automation", "status": "active", "description": "Processos - automacoes"},
            {"name": "app_integration", "status": "active", "description": "Conector de apps"},
            {"name": "church", "status": "active", "description": "Gestao de igreja"},
        ],
        "endpoints": {
            "process": "POST /api/agents/process",
            "church_chat": "POST /api/agents/church/chat",
            "church_members": "GET /api/agents/church/members",
            "church_search": "GET /api/agents/church/members/search",
            "apps": "GET /api/agents/apps",
            "skills": "GET /api/agents/skills",
        },
    }
