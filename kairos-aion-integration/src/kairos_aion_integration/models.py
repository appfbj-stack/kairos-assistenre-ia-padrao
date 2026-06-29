from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class CapabilityType(str, Enum):
    SKILL = "skill"
    MCP = "mcp"
    AGENT = "agent"


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    APPROVAL_REQUIRED = "approval_required"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


@dataclass
class AionCapability:
    id: str
    name: str
    description: str
    type: CapabilityType
    provider: str = "Aion"
    parameters: list[dict] = field(default_factory=list)
    is_active: bool = True
    metadata: dict = field(default_factory=dict)


@dataclass
class AionSkill:
    id: str
    name: str
    description: str
    parameters: list[dict] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    is_active: bool = True
    source: str = "Aion"
    category: str = "general"
    metadata: dict = field(default_factory=dict)


@dataclass
class AionMCP:
    id: str
    name: str
    description: str
    endpoint: str
    auth_type: str = "none"
    tools: list[dict] = field(default_factory=list)
    is_connected: bool = False
    is_active: bool = True
    metadata: dict = field(default_factory=dict)


@dataclass
class AionAgent:
    id: str
    name: str
    description: str
    capabilities: list[str] = field(default_factory=list)
    type: str = "general"
    model: str = "openrouter/auto"
    is_active: bool = True
    metadata: dict = field(default_factory=dict)

    def can_handle(self, intent: str) -> bool:
        intent_lower = intent.lower()
        for cap in self.capabilities:
            if cap.lower() in intent_lower:
                return True
        return False


@dataclass
class AionSession:
    id: str
    token: str
    created_at: datetime
    expires_at: datetime
    is_valid: bool = True


@dataclass
class AionTask:
    id: str
    session_id: str
    capability_type: CapabilityType
    capability_name: str
    input_data: dict
    status: ExecutionStatus = ExecutionStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None


@dataclass
class TaskResult:
    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None
    requires_approval: bool = False
    approval_id: Optional[str] = None
