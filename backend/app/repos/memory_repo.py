from typing import Optional
from core.domain.entities.memory import MemoryEntry
from core.domain.interfaces.memory_port import MemoryPort
from sqlalchemy import select, delete


class SQLAlchemyMemoryRepo(MemoryPort):
    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def store(self, entry: MemoryEntry) -> MemoryEntry:
        async with self._session_factory() as session:
            from app.models import Memory as MemModel
            row = MemModel(
                conversation_id=entry.conversation_id,
                user_id=entry.user_id,
                tenant_id=entry.tenant_id,
                key=entry.key,
                value=entry.value,
                type=entry.type,
            )
            session.add(row)
            await session.commit()
            entry.id = str(row.id)
            return entry

    async def get(self, key: str, user_id: Optional[str] = None, tenant_id: Optional[str] = None) -> Optional[str]:
        async with self._session_factory() as session:
            from app.models import Memory as MemModel
            q = select(MemModel).where(MemModel.key == key)
            if user_id:
                q = q.where(MemModel.user_id == user_id)
            if tenant_id:
                q = q.where(MemModel.tenant_id == tenant_id)
            result = await session.execute(q.order_by(MemModel.created_at.desc()).limit(1))
            row = result.scalar_one_or_none()
            return row.value if row else None

    async def list_by_type(self, type: str, user_id: Optional[str] = None, tenant_id: Optional[str] = None) -> list[MemoryEntry]:
        async with self._session_factory() as session:
            from app.models import Memory as MemModel
            q = select(MemModel).where(MemModel.type == type)
            if user_id:
                q = q.where(MemModel.user_id == user_id)
            if tenant_id:
                q = q.where(MemModel.tenant_id == tenant_id)
            result = await session.execute(q.order_by(MemModel.created_at.desc()))
            return [
                MemoryEntry(
                    id=str(r.id), key=r.key, value=r.value,
                    type=r.type, user_id=r.user_id, tenant_id=r.tenant_id,
                )
                for r in result.scalars().all()
            ]

    async def delete(self, key: str, user_id: Optional[str] = None) -> None:
        async with self._session_factory() as session:
            from app.models import Memory as MemModel
            q = delete(MemModel).where(MemModel.key == key)
            if user_id:
                q = q.where(MemModel.user_id == user_id)
            await session.execute(q)
            await session.commit()

    async def clear_session(self, user_id: str) -> None:
        async with self._session_factory() as session:
            from app.models import Memory as MemModel
            await session.execute(
                delete(MemModel).where(MemModel.user_id == user_id, MemModel.type == "session")
            )
            await session.commit()
