from core.domain.entities.context import RuntimeContext, TenantContext, UserContext, AppContext, SessionContext, PermissionContext, UserRole


class ContextManager:
    def __init__(self):
        self._store: dict[str, RuntimeContext] = {}

    def set(self, key: str, ctx: RuntimeContext):
        self._store[key] = ctx

    def get(self, key: str) -> RuntimeContext | None:
        return self._store.get(key)

    def build(
        self,
        tenant_id: str,
        tenant_name: str,
        tenant_slug: str,
        user_id: str,
        user_name: str,
        user_email: str,
        user_role: str = "member",
        app_id: str = "",
        app_name: str = "",
        app_slug: str = "",
        app_context: str = "",
        modules: list[str] | None = None,
        departments: list[str] | None = None,
        locale: str = "pt-BR",
        theme: str = "dark",
        extra: dict | None = None,
    ) -> RuntimeContext:
        return RuntimeContext(
            tenant=TenantContext(id=tenant_id, name=tenant_name, slug=tenant_slug),
            user=UserContext(id=user_id, name=user_name, email=user_email, role=UserRole(user_role)),
            app=AppContext(id=app_id, name=app_name, slug=app_slug, context=app_context),
            session=SessionContext(locale=locale, theme=theme, extra=extra or {}),
            permissions=PermissionContext(modules=modules or [], departments=departments or []),
        )

    def update(self, key: str, **kwargs):
        ctx = self._store.get(key)
        if not ctx:
            return
        for k, v in kwargs.items():
            if hasattr(ctx, k):
                setattr(ctx, k, v)
            elif k.startswith("session_"):
                setattr(ctx.session, k[8:], v)
            elif k.startswith("extra_"):
                ctx.session.extra[k[6:]] = v
