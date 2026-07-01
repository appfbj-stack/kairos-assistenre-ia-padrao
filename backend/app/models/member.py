import uuid
from datetime import datetime, date
from sqlalchemy import String, Date, DateTime, Boolean, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
import enum


class EstadoCivil(str, enum.Enum):
      solteiro = "solteiro"
      casado = "casado"
      divorciado = "divorciado"
      viuvo = "viuvo"
      uniao_estavel = "uniao_estavel"


class Member(Base):
      __tablename__ = "members"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    data_nascimento: Mapped[date | None] = mapped_column(Date, nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    whatsapp: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    endereco: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado_civil: Mapped[str | None] = mapped_column(String(20), nullable=True)
    congregacao: Mapped[str | None] = mapped_column(String(255), nullable=True)
    data_entrada: Mapped[date | None] = mapped_column(Date, nullable=True)
    batismo: Mapped[bool] = mapped_column(Boolean, default=False)
    data_batismo: Mapped[date | None] = mapped_column(Date, nullable=True)
    ministerio: Mapped[str | None] = mapped_column(String(255), nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
