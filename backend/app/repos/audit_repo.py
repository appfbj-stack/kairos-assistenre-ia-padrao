import json
from typing import Optional
from sqlalchemy import select, func, desc
from core.domain.interfaces.audit_port import AuditPort, AuditEntry


class SQLAlchemyAuditRepo(AuditPort):
    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def record(self, entry: AuditEntry) -> AuditEntry:
        async with self._session_factory() as session:
            from app.models import AuditLog
            row = AuditLog(
                tenant_id=entry.tenant_id,
                user_id=entry.user_id,
                user_name=entry.user_name,
                user_role=entry.user_role,
                event_type=entry.event_type,
                tool_name=entry.tool_name,
                app_slug=entry.app_slug,
                input_data=entry.input_data,
                result=entry.result,
                success=entry.success,
                ip_address=entry.ip_address,
            )
            session.add(row)
            await session.commit()
            entry.id = str(row.id)
            return entry

    async def query(
        self,
        tenant_id: str,
        event_type: Optional[str] = None,
        user_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditEntry]:
        async with self._session_factory() as session:
            from app.models import AuditLog
            q = select(AuditLog).where(AuditLog.tenant_id == tenant_id)
            if event_type:
                q = q.where(AuditLog.event_type == event_type)
            if user_id:
                q = q.where(AuditLog.user_id == user_id)
            if tool_name:
                q = q.where(AuditLog.tool_name == tool_name)
            q = q.order_by(desc(AuditLog.created_at)).limit(limit).offset(offset)
            result = await session.execute(q)
            return [
                AuditEntry(
                    id=str(r.id),
                    tenant_id=str(r.tenant_id),
                    user_id=r.user_id,
                    user_name=r.user_name,
                    user_role=r.user_role,
                    event_type=r.event_type,
                    tool_name=r.tool_name,
                    app_slug=r.app_slug,
                    input_data=r.input_data,
                    result=r.result,
                    success=r.success,
                    ip_address=r.ip_address,
                    created_at=str(r.created_at) if r.created_at else None,
                )
                for r in result.scalars().all()
            ]

    async def count(
        self,
        tenant_id: str,
        event_type: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> int:
        async with self._session_factory() as session:
            from app.models import AuditLog
            q = select(func.count()).select_from(AuditLog).where(AuditLog.tenant_id == tenant_id)
            if event_type:
                q = q.where(AuditLog.event_type == event_type)
            if user_id:
                q = q.where(AuditLog.user_id == user_id)
            result = await session.execute(q)
            return result.scalar() or 0
