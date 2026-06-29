from __future__ import annotations
import uuid
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class ApprovalRequest:
    id: str
    capability_name: str
    capability_type: str
    input_data: dict
    requested_by: str
    tenant_id: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    decided_at: Optional[str] = None
    decided_by: Optional[str] = None


_DANGEROUS_ACTIONS = {
    "enviar_email",
    "salvar_arquivo",
    "excluir_arquivo",
    "criar_evento",
    "enviar_mensagem",
    "executar_comando",
    "instalar_skill",
}


class AionSecurity:
    def __init__(self):
        self._approvals: dict[str, ApprovalRequest] = {}

    def requires_approval(self, tool_name: str) -> bool:
        for dangerous in _DANGEROUS_ACTIONS:
            if dangerous in tool_name.lower():
                return True
        return False

    def request_approval(
        self,
        capability_name: str,
        capability_type: str,
        input_data: dict,
        requested_by: str,
        tenant_id: str,
    ) -> ApprovalRequest:
        req = ApprovalRequest(
            id=str(uuid.uuid4()),
            capability_name=capability_name,
            capability_type=capability_type,
            input_data=input_data,
            requested_by=requested_by,
            tenant_id=tenant_id,
        )
        self._approvals[req.id] = req
        return req

    def approve(self, approval_id: str, decided_by: str) -> Optional[ApprovalRequest]:
        req = self._approvals.get(approval_id)
        if req and req.status == ApprovalStatus.PENDING:
            req.status = ApprovalStatus.APPROVED
            req.decided_at = datetime.utcnow().isoformat()
            req.decided_by = decided_by
            return req
        return None

    def reject(self, approval_id: str, decided_by: str) -> Optional[ApprovalRequest]:
        req = self._approvals.get(approval_id)
        if req and req.status == ApprovalStatus.PENDING:
            req.status = ApprovalStatus.REJECTED
            req.decided_at = datetime.utcnow().isoformat()
            req.decided_by = decided_by
            return req
        return None

    def get_pending_approvals(self, tenant_id: str) -> list[ApprovalRequest]:
        return [
            r for r in self._approvals.values()
            if r.tenant_id == tenant_id and r.status == ApprovalStatus.PENDING
        ]

    def log_action(self, action: str, details: dict) -> dict:
        return {
            "action": action,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
        }
