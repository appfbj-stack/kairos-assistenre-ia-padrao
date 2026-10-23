"""
Tenant guard - autenticacao global da API.

Problema corrigido (2026-10-23):
as rotas /api/members (CRUD de membros da igreja), /api/aion/* e
/api/agents/* nao validavam o Bearer token do tenant. Qualquer pessoa
na internet conseguia criar, ler, alterar e apagar membros da igreja
(POST /api/members/ devolvia 201 sem nenhuma credencial).

Este middleware centraliza a validacao: TODA rota /api/* passa a exigir
um Bearer token de tenant ativo. As rotas ja protegidas por
`resolve_tenant` continuam funcionando (validacao dupla e inofensiva).
Rotas publicas ficam na whitelist.
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy import select

from app.database import async_session
from app.models import Tenant

# Rotas liberadas (healthcheck do container + documentacao, se habilitada)
PUBLIC_PATHS = {
    "/health",
    "/api/health",
    "/docs",
    "/redoc",
    "/openapi.json",
}

_BEARER = "Bearer "


async def tenant_guard(request: Request, call_next):
    path = request.url.path

    # Fora do namespace /api/ nao ha dado sensivel (health, docs, assets).
    if not path.startswith("/api/"):
        return await call_next(request)

    if path in PUBLIC_PATHS:
        return await call_next(request)

    authorization = request.headers.get("authorization")
    if not authorization or not authorization.startswith(_BEARER):
        return JSONResponse(
            status_code=401,
            content={"detail": "Missing API key"},
        )

    api_key = authorization[len(_BEARER):].strip()
    if not api_key:
        return JSONResponse(
            status_code=401,
            content={"detail": "Missing API key"},
        )

    try:
        async with async_session() as session:
            result = await session.execute(
                select(Tenant).where(
                    Tenant.api_key == api_key,
                    Tenant.is_active == True,  # noqa: E712
                )
            )
            tenant = result.scalar_one_or_none()
    except Exception:
        # Falha de banco nao pode virar rota aberta.
        return JSONResponse(
            status_code=503,
            content={"detail": "Auth service unavailable"},
        )

    if not tenant:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid API key"},
        )

    request.state.tenant = tenant
    return await call_next(request)
