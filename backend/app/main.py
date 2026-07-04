from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import init_db, async_session
from app.routes.health import router as health_router
from app.routes.chat import router as chat_router
from app.routes.tools import router as tools_router
from app.routes.audit import router as audit_router
from app.routes.apps import router as apps_router
from app.routes.agent_ws import router as agent_router
from app.routes.multimodal import router as multimodal_router
from app.routes.aion import router as aion_router
from app.routes.members import router as members_router
from app.routes.langgraph_agent import router as langgraph_router
from core.container import Container
from app.repos.conversation_repo import SQLAlchemyConversationRepo
from app.repos.memory_repo import SQLAlchemyMemoryRepo
from app.repos.tool_repo import SQLAlchemyToolRepo
from app.repos.app_repo import SQLAlchemyAppRepo
from app.repos.audit_repo import SQLAlchemyAuditRepo
from app.repos.openrouter_llm import OpenRouterLLM
from core.domain.entities.app import (
    AppDef, AppModule, AppPermission, SupportedResource,
    AppEnvironment,
)


async def _auto_register_apps(container):
    if not container.app_registry or not container.app_repo:
        return
    try:
        from app.models import Tenant, App as AppModel
        from sqlalchemy import select
        async with async_session() as session:
            result = await session.execute(
                select(Tenant).where(Tenant.is_active == True)
            )
            tenants = result.scalars().all()

        for tenant in tenants:
            existing = await container.app_registry.get_by_slug(str(tenant.id), "kairos-igreja")
            if existing:
                continue

            app = AppDef(
                id="",
                tenant_id=str(tenant.id),
                name="Kairós Igreja",
                slug="kairos-igreja",
                version=settings.app_version if hasattr(settings, "app_version") else "2.0.0",
                company="Kairós Tecnologia",
                api_url="",
                environment=AppEnvironment.PRODUCTION,
                icon="Church",
                primary_color="#1e40af",
                status="active",
                origin_url="",
                context="Assistente inteligente para gestão eclesiástica",
                modules=[
                    AppModule(name="membros", description="Gestão de membros"),
                    AppModule(name="financeiro", description="Gestão financeira"),
                    AppModule(name="agenda", description="Agenda e eventos"),
                    AppModule(name="relatorios", description="Relatórios e análises"),
                ],
                permissions=[
                    AppPermission(key="membros.view", name="Ver membros", module="membros"),
                    AppPermission(key="membros.edit", name="Editar membros", module="membros"),
                    AppPermission(key="financeiro.view", name="Ver financeiro", module="financeiro"),
                    AppPermission(key="financeiro.edit", name="Editar financeiro", module="financeiro"),
                    AppPermission(key="agenda.view", name="Ver agenda", module="agenda"),
                    AppPermission(key="agenda.edit", name="Editar agenda", module="agenda"),
                    AppPermission(key="admin", name="Acesso total", module="admin"),
                ],
                supported_resources=[
                    SupportedResource.VOICE,
                    SupportedResource.IMAGE,
                    SupportedResource.DOCUMENT,
                    SupportedResource.AGENT,
                ],
            )
            await container.app_registry.register(app)
    except Exception:
        pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    container = Container(
        conversation_repo=SQLAlchemyConversationRepo(async_session),
        memory_repo=SQLAlchemyMemoryRepo(async_session),
        tool_repo=SQLAlchemyToolRepo(async_session),
        app_repo=SQLAlchemyAppRepo(async_session),
        audit_repo=SQLAlchemyAuditRepo(async_session),
        llm=OpenRouterLLM(),
        openrouter_key=settings.openrouter_api_key,
        aion_base_url=settings.aion_base_url,
        aion_api_key=settings.aion_api_key,
    ).build()
    app.state.container = container
    if container.aion_integration:
        try:
            await container.aion_integration.initialize()
        except Exception:
            pass
    await _auto_register_apps(container)
    yield

app = FastAPI(
    title=settings.app_name,
    description="Kairos Assistant API - Powered by Aion Multi-Agent System",
    version="2.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas existentes
app.include_router(health_router)
app.include_router(chat_router)
app.include_router(tools_router)
app.include_router(audit_router)
app.include_router(apps_router)
app.include_router(agent_router)
app.include_router(multimodal_router)
app.include_router(aion_router)

# Novas rotas - Sistema de Agentes Aion
app.include_router(members_router)      # CRUD de membros da igreja
app.include_router(langgraph_router)    # Sistema multi-agente LangGraph
