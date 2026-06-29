from typing import Optional
from core.domain.entities.tool import ToolDef, ToolParameter
from core.domain.interfaces.tool_port import ToolPort
from sqlalchemy import select
import json
import httpx


class SQLAlchemyToolRepo(ToolPort):
    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def register(self, tool: ToolDef) -> ToolDef:
        async with self._session_factory() as session:
            from app.models import Tool as ToolModel
            row = ToolModel(
                app_id=tool.app_id,
                name=tool.name,
                description=tool.description,
                schema_json=json.dumps({
                    "properties": {p.name: {"type": p.type, "description": p.description} for p in tool.parameters},
                    "required": [p.name for p in tool.parameters if p.required],
                }),
                endpoint=tool.endpoint,
                method=tool.method,
                headers_json=json.dumps(tool.headers),
            )
            session.add(row)
            await session.commit()
            tool.id = str(row.id)
            return tool

    async def get_by_id(self, tool_id: str) -> Optional[ToolDef]:
        async with self._session_factory() as session:
            from app.models import Tool as ToolModel
            result = await session.execute(select(ToolModel).where(ToolModel.id == tool_id))
            row = result.scalar_one_or_none()
            return self._row_to_tool(row) if row else None

    async def get_by_name(self, app_id: str, name: str) -> Optional[ToolDef]:
        async with self._session_factory() as session:
            from app.models import Tool as ToolModel
            result = await session.execute(
                select(ToolModel).where(ToolModel.app_id == app_id, ToolModel.name == name)
            )
            row = result.scalar_one_or_none()
            return self._row_to_tool(row) if row else None

    async def list_by_app(self, app_id: str) -> list[ToolDef]:
        async with self._session_factory() as session:
            from app.models import Tool as ToolModel
            result = await session.execute(
                select(ToolModel).where(ToolModel.app_id == app_id, ToolModel.is_active == True)
            )
            return [self._row_to_tool(r) for r in result.scalars().all()]

    async def list_by_tenant(self, tenant_id: str) -> list[ToolDef]:
        async with self._session_factory() as session:
            from app.models import Tool as ToolModel, App
            result = await session.execute(
                select(ToolModel).join(App).where(App.tenant_id == tenant_id, ToolModel.is_active == True)
            )
            return [self._row_to_tool(r) for r in result.scalars().all()]

    async def execute(self, tool: ToolDef, args: dict) -> dict:
        headers = tool.headers
        async with httpx.AsyncClient(timeout=30) as client:
            if tool.method.upper() == "GET":
                resp = await client.get(tool.endpoint, params=args, headers=headers)
            else:
                resp = await client.post(tool.endpoint, json=args, headers=headers)
            return {"status": resp.status_code, "data": resp.json()}

    async def delete(self, tool_id: str) -> None:
        async with self._session_factory() as session:
            from app.models import Tool as ToolModel
            result = await session.execute(select(ToolModel).where(ToolModel.id == tool_id))
            row = result.scalar_one_or_none()
            if row:
                await session.delete(row)
                await session.commit()

    def _row_to_tool(self, row) -> ToolDef:
        schema = json.loads(row.schema_json)
        params = []
        for name, prop in schema.get("properties", {}).items():
            params.append(ToolParameter(
                name=name,
                type=prop.get("type", "string"),
                description=prop.get("description", ""),
                required=name in schema.get("required", []),
            ))
        return ToolDef(
            id=str(row.id),
            app_id=str(row.app_id),
            name=row.name,
            description=row.description,
            parameters=params,
            endpoint=row.endpoint,
            method=row.method,
            headers=json.loads(row.headers_json),
            is_active=row.is_active,
        )
