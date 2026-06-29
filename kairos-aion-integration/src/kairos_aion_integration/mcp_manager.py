from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from .models import AionMCP, TaskResult


@dataclass
class MCPConnection:
    name: str
    endpoint: str
    auth_type: str
    connected_at: str = ""
    is_healthy: bool = False
    tools_count: int = 0


class AionMCPServer:
    def __init__(self, mcp: AionMCP):
        self.mcp = mcp
        self._connection: Optional[MCPConnection] = None

    async def connect(self) -> MCPConnection:
        self._connection = MCPConnection(
            name=self.mcp.name,
            endpoint=self.mcp.endpoint,
            auth_type=self.mcp.auth_type,
            connected_at=datetime.utcnow().isoformat(),
            is_healthy=True,
            tools_count=len(self.mcp.tools),
        )
        return self._connection

    def disconnect(self):
        self._connection = None

    @property
    def is_connected(self) -> bool:
        return self._connection is not None

    def get_tools(self) -> list[dict]:
        return self.mcp.tools

    def get_tool(self, tool_name: str) -> Optional[dict]:
        for t in self.mcp.tools:
            if t.get("name") == tool_name:
                return t
        return None


class MCPManager:
    def __init__(self):
        self._servers: dict[str, AionMCPServer] = {}

    def register(self, mcp: AionMCP):
        self._servers[mcp.name] = AionMCPServer(mcp)

    def register_batch(self, mcps: list[AionMCP]):
        for m in mcps:
            self.register(m)

    def get(self, name: str) -> Optional[AionMCPServer]:
        return self._servers.get(name)

    def list(self) -> list[AionMCPServer]:
        return list(self._servers.values())

    def list_connected(self) -> list[AionMCPServer]:
        return [s for s in self._servers.values() if s.is_connected]

    def list_connections(self) -> list[MCPConnection]:
        return [s._connection for s in self._servers.values() if s._connection]

    def to_openai_tools(self) -> list[dict]:
        tools = []
        for server in self._servers.values():
            for t in server.get_tools():
                name = t.get("name", "")
                desc = t.get("description", "")
                params = t.get("parameters", {})
                properties = {}
                required = []
                for pname, ptype in params.items():
                    properties[pname] = {"type": ptype if isinstance(ptype, str) else "string"}
                schema = {"type": "object", "properties": properties}
                if required:
                    schema["required"] = required
                tools.append({
                    "type": "function",
                    "function": {
                        "name": f"mcp_{server.mcp.name}_{name}",
                        "description": f"[MCP {server.mcp.name}] {desc}",
                        "parameters": schema,
                    },
                })
        return tools
