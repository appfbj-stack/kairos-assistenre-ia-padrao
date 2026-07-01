import uuid
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.models.member import Member


async def create_member(session: AsyncSession, data: dict) -> Member:
      member = Member(
                id=str(uuid.uuid4()),
                nome=data.get("nome", ""),
                data_nascimento=data.get("data_nascimento"),
                telefone=data.get("telefone"),
                whatsapp=data.get("whatsapp"),
                email=data.get("email"),
                endereco=data.get("endereco"),
                estado_civil=data.get("estado_civil"),
                congregacao=data.get("congregacao"),
                data_entrada=data.get("data_entrada"),
                batismo=data.get("batismo", False),
                data_batismo=data.get("data_batismo"),
                ministerio=data.get("ministerio"),
                observacoes=data.get("observacoes"),
                ativo=True,
                created_by=data.get("created_by"),
      )
      session.add(member)
      await session.commit()
      await session.refresh(member)
      return member


async def update_member(session: AsyncSession, member_id: str, data: dict) -> Optional[Member]:
      result = await session.execute(select(Member).where(Member.id == member_id))
      member = result.scalar_one_or_none()
      if not member:
                return None
            for key, value in data.items():
                      if hasattr(member, key) and value is not None:
                                    setattr(member, key, value)
                            member.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(member)
    return member


async def search_member(session: AsyncSession, query: str) -> List[Member]:
      result = await session.execute(
                select(Member).where(
                              or_(
                                                Member.nome.ilike(f"%{query}%"),
                                                Member.email.ilike(f"%{query}%"),
                                                Member.telefone.ilike(f"%{query}%"),
                                                Member.whatsapp.ilike(f"%{query}%"),
                              )
                ).limit(20)
      )
    return list(result.scalars().all())


async def get_member(session: AsyncSession, member_id: str) -> Optional[Member]:
      result = await session.execute(select(Member).where(Member.id == member_id))
    return result.scalar_one_or_none()


async def list_members(session: AsyncSession, congregacao: Optional[str] = None, ativo: bool = True) -> List[Member]:
      query = select(Member).where(Member.ativo == ativo)
    if congregacao:
              query = query.where(Member.congregacao == congregacao)
    result = await session.execute(query.order_by(Member.nome))
    return list(result.scalars().all())


async def delete_member(session: AsyncSession, member_id: str) -> bool:
      result = await session.execute(select(Member).where(Member.id == member_id))
    member = result.scalar_one_or_none()
    if not member:
              return False
    member.ativo = False
    member.updated_at = datetime.utcnow()
    await session.commit()
    return True
