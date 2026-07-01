"""
Aion Church Agent - Agente especialista para gestao de igreja.
Conduz o usuario de forma conversacional para cadastrar e gerenciar membros.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, date
from typing import Optional
import logging

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = ["nome"]

MEMBER_FIELDS = [
    {"key": "nome",           "label": "Nome completo",            "required": True,  "type": "str"},
    {"key": "data_nascimento","label": "Data de nascimento",       "required": False, "type": "date", "hint": "DD/MM/AAAA"},
    {"key": "telefone",       "label": "Telefone",                 "required": False, "type": "str"},
    {"key": "whatsapp",       "label": "WhatsApp",                 "required": False, "type": "str"},
    {"key": "email",          "label": "E-mail",                   "required": False, "type": "str"},
    {"key": "endereco",       "label": "Endereco completo",        "required": False, "type": "str"},
    {"key": "estado_civil",   "label": "Estado civil",             "required": False, "type": "enum",
     "options": ["solteiro", "casado", "divorciado", "viuvo", "uniao_estavel"]},
    {"key": "congregacao",    "label": "Congregacao",              "required": False, "type": "str"},
    {"key": "data_entrada",   "label": "Data de entrada na igreja","required": False, "type": "date", "hint": "DD/MM/AAAA"},
    {"key": "batismo",        "label": "E batizado?",              "required": False, "type": "bool"},
    {"key": "ministerio",     "label": "Ministerio/Area",          "required": False, "type": "str"},
    {"key": "observacoes",    "label": "Observacoes",              "required": False, "type": "str"},
]


def _parse_date(value: str):
    formats = ["%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d", "%d-%m-%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(value.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def _parse_bool(value: str) -> bool:
    return value.lower().strip() in ["sim", "s", "yes", "y", "true", "1", "batizado"]


def _validate_email(email: str) -> bool:
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


class MemberRegistrationContext:
    def __init__(self):
        self.collected: dict = {}
        self.current_field_index: int = 0
        self.confirmed: bool = False
        self.cancelled: bool = False
        self.errors: list = []
        self.started_at: datetime = datetime.utcnow()

    def get_current_field(self):
        if self.current_field_index < len(MEMBER_FIELDS):
            return MEMBER_FIELDS[self.current_field_index]
        return None

    def advance(self):
        self.current_field_index += 1

    def is_complete(self) -> bool:
        required_done = all(self.collected.get(f["key"]) for f in MEMBER_FIELDS if f["required"])
        return required_done and self.current_field_index >= len(MEMBER_FIELDS)

    def to_member_dict(self) -> dict:
        return dict(self.collected)


class AionChurchAgent:
    """Agente especialista em gestao de igreja com cadastro conversacional."""

    _sessions: dict = {}

    def __init__(self, db_session=None):
        self.db_session = db_session

    async def handle_message(self, message: str, session_id: str) -> dict:
        msg = message.strip().lower()

        if self._is_cancel(msg):
            return self._cancel_session(session_id)

        if session_id not in self._sessions:
            if self._is_cadastro_intent(message):
                return self._start_registration(session_id)
            return self._help_response()

        ctx = self._sessions[session_id]

        if self._is_cancel(msg):
            return self._cancel_session(session_id)

        field = ctx.get_current_field()

        if field:
            if self._is_skip(msg) and not field.get("required"):
                ctx.advance()
            else:
                result = self._process_field_answer(field, message, ctx)
                if not result["valid"]:
                    return {
                        "response": result["error"],
                        "action": "ask_again",
                        "field": field["key"],
                        "session_id": session_id,
                    }
                ctx.advance()

        if ctx.is_complete():
            return await self._confirm_registration(ctx, session_id, message)

        return self._ask_next_field(ctx, session_id)

    def _is_cadastro_intent(self, message: str) -> bool:
        keywords = ["cadastrar", "cadastro", "novo membro", "adicionar membro",
                    "registrar membro", "incluir membro", "quero cadastrar"]
        return any(kw in message.lower() for kw in keywords)

    def _is_cancel(self, msg: str) -> bool:
        return any(kw in msg for kw in ["cancelar", "cancel", "parar", "sair", "abort"])

    def _is_skip(self, msg: str) -> bool:
        return any(kw in msg for kw in ["pular", "skip", "nao sei", "nao tenho", "nenhum"])

    def _start_registration(self, session_id: str) -> dict:
        ctx = MemberRegistrationContext()
        self._sessions[session_id] = ctx
        field = ctx.get_current_field()
        return {
            "response": (
                "Otimo! Vou ajudar a cadastrar um novo membro.\n\n"
                f"Vamos comecar. {self._field_prompt(field)}\n\n"
                "Dica: Digite 'pular' para campos opcionais ou 'cancelar' para encerrar."
            ),
            "action": "collecting",
            "field": field["key"],
            "session_id": session_id,
            "progress": f"1/{len(MEMBER_FIELDS)}",
        }

    def _ask_next_field(self, ctx: MemberRegistrationContext, session_id: str) -> dict:
        field = ctx.get_current_field()
        if not field:
            return {"response": "Todos os dados coletados!", "action": "done", "session_id": session_id}
        total = len(MEMBER_FIELDS)
        current = ctx.current_field_index + 1
        optional_hint = " (opcional - 'pular' para deixar em branco)" if not field.get("required") else ""
        return {
            "response": f"[{current}/{total}] {self._field_prompt(field)}{optional_hint}",
            "action": "collecting",
            "field": field["key"],
            "session_id": session_id,
            "progress": f"{current}/{total}",
        }

    def _field_prompt(self, field: dict) -> str:
        prompt = f"{field['label']}:"
        if field.get("hint"):
            prompt += f" ({field['hint']})"
        if field.get("options"):
            prompt += f"\nOpcoes: {', '.join(field['options'])}"
        return prompt

    def _process_field_answer(self, field: dict, answer: str, ctx) -> dict:
        key = field["key"]
        ftype = field.get("type", "str")
        answer = answer.strip()
        if ftype == "date":
            parsed = _parse_date(answer)
            if not parsed:
                return {"valid": False, "error": "Data invalida. Use DD/MM/AAAA. Tente novamente:"}
            ctx.collected[key] = parsed
            return {"valid": True}
        if ftype == "bool":
            ctx.collected[key] = _parse_bool(answer)
            return {"valid": True}
        if ftype == "enum":
            options = field.get("options", [])
            match = next((o for o in options if answer.lower().startswith(o[:3])), None)
            if not match:
                return {"valid": False, "error": f"Opcao invalida. Escolha: {', '.join(options)}"}
            ctx.collected[key] = match
            return {"valid": True}
        if key == "email" and answer and not _validate_email(answer):
            return {"valid": False, "error": "E-mail invalido. Informe um e-mail valido ou 'pular':"}
        ctx.collected[key] = answer
        return {"valid": True}

    async def _confirm_registration(self, ctx, session_id: str, message: str) -> dict:
        if ctx.confirmed:
            return await self._save_member(ctx, session_id)
        msg = message.lower().strip()
        if any(kw in msg for kw in ["sim", "confirmar", "salvar", "ok", "correto"]):
            ctx.confirmed = True
            return await self._save_member(ctx, session_id)
        if any(kw in msg for kw in ["nao", "editar", "corrigir", "voltar"]):
            ctx.current_field_index = 0
            ctx.confirmed = False
            return {
                "response": "Ok! Vamos preencher novamente.\n\n" + self._field_prompt(ctx.get_current_field()),
                "action": "collecting",
                "field": ctx.get_current_field()["key"],
                "session_id": session_id,
            }
        summary = self._build_summary(ctx)
        return {
            "response": f"Resumo do membro:\n\n{summary}\n\nConfirma o cadastro? (sim/nao)",
            "action": "awaiting_confirmation",
            "data": ctx.collected,
            "session_id": session_id,
        }

    def _build_summary(self, ctx) -> str:
        lines = []
        for field in MEMBER_FIELDS:
            value = ctx.collected.get(field["key"])
            if value is not None:
                display = "Sim" if value is True else ("Nao" if value is False else str(value))
                lines.append(f"- {field['label']}: {display}")
        return "\n".join(lines)

    async def _save_member(self, ctx, session_id: str) -> dict:
        try:
            if self.db_session:
                from app.services.member_service import create_member
                member = await create_member(self.db_session, ctx.to_member_dict())
                member_id = member.id
            else:
                member_id = f"sim-{session_id[:8]}"
            del self._sessions[session_id]
            nome = ctx.collected.get("nome", "")
            return {
                "response": (
                    f"Membro {nome} cadastrado com sucesso!\n"
                    f"ID: {member_id}\n\n"
                    "O que deseja fazer agora?\n"
                    "- Cadastrar outro membro\n"
                    "- Buscar um membro\n"
                    "- Listar membros"
                ),
                "action": "saved",
                "member_id": member_id,
                "session_id": session_id,
                "data": ctx.collected,
            }
        except Exception as e:
            logger.error(f"[ChurchAgent] Erro ao salvar: {e}")
            return {"response": f"Erro ao salvar: {e}", "action": "error", "session_id": session_id}

    def _cancel_session(self, session_id: str) -> dict:
        if session_id in self._sessions:
            del self._sessions[session_id]
        return {"response": "Cadastro cancelado. Como posso ajudar?", "action": "cancelled", "session_id": session_id}

    def _help_response(self) -> dict:
        return {
            "response": (
                "Sou o Aion Church Agent. Posso ajudar com:\n\n"
                "- Cadastrar membro: 'Quero cadastrar um membro'\n"
                "- Buscar membro: 'Buscar membro Joao Silva'\n"
                "- Listar membros: 'Listar membros da Sede'\n\n"
                "Como posso ajudar?"
            ),
            "action": "help",
        }

    async def search_members(self, query: str) -> dict:
        if self.db_session:
            from app.services.member_service import search_member
            members = await search_member(self.db_session, query)
            if not members:
                return {"response": f"Nenhum membro encontrado para '{query}'.", "members": []}
            lines = [f"- {m.nome} | {m.congregacao or '-'} | {m.telefone or '-'}" for m in members]
            return {
                "response": f"Encontrei {len(members)} membro(s):\n\n" + "\n".join(lines),
                "members": [{"id": m.id, "nome": m.nome} for m in members],
            }
        return {"response": "Servico de busca nao disponivel.", "members": []}

    async def list_members(self, congregacao=None) -> dict:
        if self.db_session:
            from app.services.member_service import list_members
            members = await list_members(self.db_session, congregacao=congregacao)
            if not members:
                return {"response": "Nenhum membro encontrado.", "members": []}
            lines = [f"{i+1}. {m.nome} | {m.congregacao or '-'}" for i, m in enumerate(members)]
            return {
                "response": f"Total: {len(members)} membro(s)\n\n" + "\n".join(lines),
                "members": [{"id": m.id, "nome": m.nome} for m in members],
            }
        return {"response": "Servico nao disponivel.", "members": []}
