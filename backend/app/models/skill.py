import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Skill(Base):
      __tablename__ = "skills"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    versao: Mapped[str] = mapped_column(String(20), default="1.0.0")
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    categoria: Mapped[str] = mapped_column(String(100), default="general")
    agente_criador: Mapped[str | None] = mapped_column(String(100), nullable=True)
    entrada_schema: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    saida_schema: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    codigo: Mapped[str | None] = mapped_column(Text, nullable=True)
    ferramentas: Mapped[list | None] = mapped_column(JSON, nullable=True)
    resultado_teste: Mapped[str | None] = mapped_column(Text, nullable=True)
    aprovada: Mapped[bool] = mapped_column(Boolean, default=False)
    ativa: Mapped[bool] = mapped_column(Boolean, default=True)
    uso_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    aprovada_por: Mapped[str | None] = mapped_column(String(100), nullable=True)
    aprovada_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
