from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    LEADER = "leader"
    MEMBER = "member"
    VIEWER = "viewer"


@dataclass
class TenantContext:
    id: str
    name: str
    slug: str


@dataclass
class UserContext:
    id: str
    name: str
    email: str
    role: UserRole = UserRole.MEMBER


@dataclass
class AppContext:
    id: str
    name: str
    slug: str
    origin_url: str = ""
    context: str = ""


@dataclass
class SessionContext:
    locale: str = "pt-BR"
    theme: str = "dark"
    extra: dict = field(default_factory=dict)


@dataclass
class PermissionContext:
    modules: list[str] = field(default_factory=list)
    departments: list[str] = field(default_factory=list)

    def can_access(self, module: str) -> bool:
        return not self.modules or module in self.modules


@dataclass
class RuntimeContext:
    tenant: TenantContext
    user: UserContext
    app: AppContext
    session: SessionContext = field(default_factory=SessionContext)
    permissions: PermissionContext = field(default_factory=PermissionContext)

    def can(self, module: str) -> bool:
        if self.user.role == UserRole.ADMIN:
            return True
        return self.permissions.can_access(module)

    @property
    def system_prompt_extra(self) -> str:
        parts = []
        if self.app.context:
            parts.append(f"App context: {self.app.context}")
        if self.session.extra:
            for k, v in self.session.extra.items():
                parts.append(f"{k}: {v}")
        return "\n".join(parts)
