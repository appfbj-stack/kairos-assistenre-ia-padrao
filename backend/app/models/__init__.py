from app.config import settings
from app.database import Base
from sqlalchemy import Column, String, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    api_key = Column(String(255), unique=True, nullable=False, index=True)
    context = Column(Text, default="")
    model = Column(String(100), default=settings.openrouter_model)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(255), default="Nova conversa")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    filename = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class App(Base):
    __tablename__ = "apps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False)
    origin_url = Column(String(500), default="")
    context = Column(Text, default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Memory(Base):
    __tablename__ = "memory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    user_id = Column(String(255), nullable=True, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    key = Column(String(255), nullable=False, index=True)
    value = Column(Text, nullable=False)
    type = Column(String(50), nullable=False, default="session")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Tool(Base):
    __tablename__ = "tools"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    app_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    schema_json = Column(Text, default="{}")
    endpoint = Column(String(500), nullable=False)
    method = Column(String(10), default="POST")
    headers_json = Column(Text, default="{}")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(String(255), nullable=True, index=True)
    user_name = Column(String(255), nullable=True)
    user_role = Column(String(50), nullable=True)
    event_type = Column(String(100), nullable=False, index=True)
    tool_name = Column(String(100), nullable=True)
    app_slug = Column(String(100), nullable=True)
    input_data = Column(Text, nullable=True)
    result = Column(Text, nullable=True)
    success = Column(Boolean, default=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
