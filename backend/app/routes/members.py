from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.member_service import (
    create_member, update_member, search_member,
    get_member, list_members, delete_member
)

router = APIRouter(prefix="/api/members", tags=["members"])


class MemberCreate(BaseModel):
      nome: str
      data_nascimento: Optional[date] = None
      telefone: Optional[str] = None
      whatsapp: Optional[str] = None
      email: Optional[str] = None
      endereco: Optional[str] = None
      estado_civil: Optional[str] = None
      congregacao: Optional[str] = None
      data_entrada: Optional[date] = None
      batismo: bool = False
      data_batismo: Optional[date] = None
      ministerio: Optional[str] = None
      observacoes: Optional[str] = None


class MemberUpdate(BaseModel):
      nome: Optional[str] = None
      data_nascimento: Optional[date] = None
      telefone: Optional[str] = None
      whatsapp: Optional[str] = None
      email: Optional[str] = None
      endereco: Optional[str] = None
      estado_civil: Optional[str] = None
      congregacao: Optional[str] = None
      data_entrada: Optional[date] = None
      batismo: Optional[bool] = None
      data_batismo: Optional[date] = None
      ministerio: Optional[str] = None
      observacoes: Optional[str] = None


def member_to_dict(m) -> dict:
      return {
                "id": m.id,
                "nome": m.nome,
                "data_nascimento": str(m.data_nascimento) if m.data_nascimento else None,
                "telefone": m.telefone,
                "whatsapp": m.whatsapp,
                "email": m.email,
                "endereco": m.endereco,
                "estado_civil": m.estado_civil,
                "congregacao": m.congregacao,
                "data_entrada": str(m.data_entrada) if m.data_entrada else None,
                "batismo": m.batismo,
                "data_batismo": str(m.data_batismo) if m.data_batismo else None,
                "ministerio": m.ministerio,
                "observacoes": m.observacoes,
                "ativo": m.ativo,
                "created_at": str(m.created_at),
                "updated_at": str(m.updated_at),
      }


@router.post("/", status_code=201)
async def criar_membro(body: MemberCreate, db: AsyncSession = Depends(get_db)):
      member = await create_member(db, body.model_dump())
      return {"success": True, "member": member_to_dict(member)}


@router.get("/")
async def listar_membros(
      congregacao: Optional[str] = Query(None),
      ativo: bool = Query(True),
      db: AsyncSession = Depends(get_db)
):
      members = await list_members(db, congregacao=congregacao, ativo=ativo)
      return {"members": [member_to_dict(m) for m in members], "total": len(members)}


@router.get("/search")
async def buscar_membros(q: str = Query(..., min_length=2), db: AsyncSession = Depends(get_db)):
      members = await search_member(db, q)
      return {"members": [member_to_dict(m) for m in members], "total": len(members)}


@router.get("/{member_id}")
async def obter_membro(member_id: str, db: AsyncSession = Depends(get_db)):
      member = await get_member(db, member_id)
      if not member:
                raise HTTPException(status_code=404, detail="Membro nao encontrado")
            return {"member": member_to_dict(member)}


@router.put("/{member_id}")
async def atualizar_membro(member_id: str, body: MemberUpdate, db: AsyncSession = Depends(get_db)):
      member = await update_member(db, member_id, body.model_dump(exclude_none=True))
    if not member:
              raise HTTPException(status_code=404, detail="Membro nao encontrado")
          return {"success": True, "member": member_to_dict(member)}


@router.delete("/{member_id}")
async def remover_membro(member_id: str, db: AsyncSession = Depends(get_db)):
      ok = await delete_member(db, member_id)
    if not ok:
              raise HTTPException(status_code=404, detail="Membro nao encontrado")
          return {"success": True, "message": "Membro desativado com sucesso"}
