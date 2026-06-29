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
from core.container import Container
from app.repos.conversation_repo import SQLAlchemyConversationRepo
from app.repos.memory_repo import SQLAlchemyMemoryRepo
from app.repos.tool_repo import SQLAlchemyToolRepo
from app.repos.audit_repo import SQLAlchemyAuditRepo
from app.repos.openrouter_llm import OpenRouterLLM
from app.routes.aion import router as aion_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    container = Container(
        conversation_repo=SQLAlchemyConversationRepo(async_session),
        memory_repo=SQLAlchemyMemoryRepo(async_session),
        tool_repo=SQLAlchemyToolRepo(async_session),
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
    yield


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(tools_router)
app.include_router(audit_router)
app.include_router(apps_router)
app.include_router(agent_router)
app.include_router(multimodal_router)
app.include_router(aion_router)
