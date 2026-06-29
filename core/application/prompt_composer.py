from typing import Optional
from core.domain.entities.context import RuntimeContext


class PromptComposer:
    def __init__(self):
        self._base_prompt = (
            "Você é o Kairos, um assistente inteligente e amigável. "
            "Responda de forma clara, direta e útil em português do Brasil."
        )
        self._system_overrides: dict[str, str] = {}

    def set_base(self, prompt: str):
        self._base_prompt = prompt

    def set_system_override(self, key: str, prompt: str):
        self._system_overrides[key] = prompt

    def compose(
        self,
        context: Optional[RuntimeContext] = None,
        app_prompt: Optional[str] = None,
        tenant_prompt: Optional[str] = None,
        session_prompt: Optional[str] = None,
    ) -> str:
        parts = [self._base_prompt]

        if context and context.app.context:
            parts.append(f"\n\nContexto do aplicativo:\n{context.app.context}")

        if tenant_prompt:
            parts.append(f"\n\nContexto do tenant:\n{tenant_prompt}")

        if context and context.user:
            parts.append(
                f"\n\nUsuário: {context.user.name} ({context.user.email}, role: {context.user.role.value})"
            )

        if context and context.session.extra:
            extra = "\n".join(f"{k}: {v}" for k, v in context.session.extra.items())
            parts.append(f"\n\nSessão:\n{extra}")

        if app_prompt:
            parts.append(f"\n\n{app_prompt}")
        if session_prompt:
            parts.append(f"\n\n{session_prompt}")

        for key in self._system_overrides:
            if key in str(context).lower() if context else False:
                parts.append(f"\n\n{self._system_overrides[key]}")

        return "\n".join(parts)
