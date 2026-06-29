from core.domain.entities.conversation import Conversation, Message, MessageRole
from core.domain.interfaces.conversation_port import ConversationPort
from typing import Optional
from sqlalchemy import select, delete


class SQLAlchemyConversationRepo(ConversationPort):
    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def create(self, conversation: Conversation) -> Conversation:
        async with self._session_factory() as session:
            from app.models import Conversation as ConvModel
            row = ConvModel(
                id=conversation.id,
                tenant_id=conversation.tenant_id,
                title=conversation.title,
            )
            session.add(row)
            await session.commit()
            return conversation

    async def get_by_id(self, conversation_id: str) -> Optional[Conversation]:
        async with self._session_factory() as session:
            from app.models import Conversation as ConvModel
            result = await session.execute(
                select(ConvModel).where(ConvModel.id == conversation_id)
            )
            row = result.scalar_one_or_none()
            if not row:
                return None
            return Conversation(
                id=str(row.id),
                tenant_id=str(row.tenant_id),
                title=row.title,
                created_at=str(row.created_at) if row.created_at else None,
            )

    async def add_message(self, message: Message) -> Message:
        async with self._session_factory() as session:
            from app.models import Message as MsgModel
            row = MsgModel(
                conversation_id=message.conversation_id,
                role=message.role.value,
                content=message.content,
            )
            session.add(row)
            await session.commit()
            message.id = str(row.id)
            return message

    async def get_messages(self, conversation_id: str) -> list[Message]:
        async with self._session_factory() as session:
            from app.models import Message as MsgModel
            result = await session.execute(
                select(MsgModel)
                .where(MsgModel.conversation_id == conversation_id)
                .order_by(MsgModel.created_at)
            )
            return [
                Message(
                    id=str(r.id),
                    conversation_id=str(r.conversation_id),
                    role=MessageRole(r.role),
                    content=r.content,
                    created_at=str(r.created_at) if r.created_at else None,
                )
                for r in result.scalars().all()
            ]

    async def list_by_tenant(self, tenant_id: str, limit: int = 50) -> list[Conversation]:
        async with self._session_factory() as session:
            from app.models import Conversation as ConvModel
            result = await session.execute(
                select(ConvModel)
                .where(ConvModel.tenant_id == tenant_id)
                .order_by(ConvModel.updated_at.desc())
                .limit(limit)
            )
            return [
                Conversation(
                    id=str(r.id),
                    tenant_id=str(r.tenant_id),
                    title=r.title,
                    created_at=str(r.created_at) if r.created_at else None,
                )
                for r in result.scalars().all()
            ]

    async def delete(self, conversation_id: str) -> None:
        async with self._session_factory() as session:
            from app.models import Message as MsgModel, Conversation as ConvModel
            await session.execute(
                delete(MsgModel).where(MsgModel.conversation_id == conversation_id)
            )
            await session.execute(
                delete(ConvModel).where(ConvModel.id == conversation_id)
            )
            await session.commit()
