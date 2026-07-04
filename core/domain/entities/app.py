from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import re


class AppStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class AppEnvironment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class SupportedResource(str, Enum):
    VOICE = "voice"
    IMAGE = "image"
    DOCUMENT = "document"
    AGENT = "agent"


@dataclass
class AppModule:
    name: str
    description: str = ""
    is_active: bool = True


@dataclass
class AppPermission:
    key: str
    name: str
    description: str = ""
    module: str = "general"


@dataclass
class AppDef:
    id: str
    tenant_id: str
    name: str
    slug: str
    version: str = "1.0.0"
    company: str = ""
    api_url: str = ""
    environment: AppEnvironment = AppEnvironment.PRODUCTION
    icon: str = ""
    primary_color: str = "#1e40af"
    status: AppStatus = AppStatus.ACTIVE
    origin_url: str = ""
    context: str = ""
    modules: list[AppModule] = field(default_factory=list)
    tools: list[dict] = field(default_factory=list)
    permissions: list[AppPermission] = field(default_factory=list)
    supported_resources: list[SupportedResource] = field(default_factory=lambda: [SupportedResource.VOICE, SupportedResource.IMAGE, SupportedResource.DOCUMENT])
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @staticmethod
    def validate_slug(slug: str) -> bool:
        return bool(re.match(r"^[a-z0-9][a-z0-9_-]{1,48}[a-z0-9]$", slug))

    @staticmethod
    def validate_version(version: str) -> bool:
        return bool(re.match(r"^\d+\.\d+\.\d+$", version))

    def to_dict(self) -> dict:
        env = self.environment.value if hasattr(self.environment, "value") else self.environment
        st = self.status.value if hasattr(self.status, "value") else self.status
        resources = [r.value if hasattr(r, "value") else r for r in self.supported_resources]
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "name": self.name,
            "slug": self.slug,
            "version": self.version,
            "company": self.company,
            "api_url": self.api_url,
            "environment": env,
            "icon": self.icon,
            "primary_color": self.primary_color,
            "status": st,
            "origin_url": self.origin_url,
            "context": self.context,
            "modules": [{"name": m.name, "description": m.description, "is_active": m.is_active} for m in self.modules],
            "tools": self.tools,
            "permissions": [{"key": p.key, "name": p.name, "description": p.description, "module": p.module} for p in self.permissions],
            "supported_resources": resources,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
