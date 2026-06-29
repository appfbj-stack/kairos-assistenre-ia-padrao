"""
Seed script for Kairos Igreja integration demo.
Creates:
- Igreja tenant with API key
- Kairos Igreja app
- Church tools (members, events, finance)

Run: python seed_igreja.py
"""
import asyncio
import uuid
import json
from app.database import async_session, init_db
from app.models import Tenant, App, Tool
from sqlalchemy import select


TOOLS_IGREJA = [
    {
        "name": "cadastrar_membro",
        "description": "Cadastra um novo membro na igreja. Parametros: nome, email, telefone, endereco, data_nascimento, cargo, departamento_id",
        "schema": {
            "type": "object",
            "properties": {
                "nome": {"type": "string", "description": "Nome completo do membro"},
                "email": {"type": "string", "description": "Email do membro"},
                "telefone": {"type": "string", "description": "Telefone de contato"},
                "endereco": {"type": "string", "description": "Endereco do membro"},
                "data_nascimento": {"type": "string", "description": "Data de nascimento (YYYY-MM-DD)"},
                "cargo": {"type": "string", "description": "Cargo na igreja (membro, lider, pastor, diacono)"},
                "departamento_id": {"type": "string", "description": "ID do departamento"},
            },
            "required": ["nome", "email"],
        },
        "endpoint": "https://api.igreja.fbautomacao.space/api/membros",
        "method": "POST",
        "module": "membros",
    },
    {
        "name": "buscar_membro",
        "description": "Busca membros por nome, email ou ID. Parametros: query (nome/email), limite",
        "schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Nome, email ou ID do membro"},
                "limite": {"type": "integer", "description": "Maximo de resultados"},
            },
            "required": ["query"],
        },
        "endpoint": "https://api.igreja.fbautomacao.space/api/membros/buscar",
        "method": "GET",
        "module": "membros",
    },
    {
        "name": "atualizar_membro",
        "description": "Atualiza dados de um membro existente. Parametros: id, campos a atualizar",
        "schema": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "ID do membro"},
                "nome": {"type": "string"},
                "email": {"type": "string"},
                "telefone": {"type": "string"},
                "endereco": {"type": "string"},
                "cargo": {"type": "string"},
            },
            "required": ["id"],
        },
        "endpoint": "https://api.igreja.fbautomacao.space/api/membros",
        "method": "PUT",
        "module": "membros",
    },
    {
        "name": "listar_aniversariantes",
        "description": "Lista aniversariantes do mes. Parametros: mes (opcional, padrao mes atual)",
        "schema": {
            "type": "object",
            "properties": {
                "mes": {"type": "integer", "description": "Numero do mes (1-12)"},
            },
        },
        "endpoint": "https://api.igreja.fbautomacao.space/api/membros/aniversariantes",
        "method": "GET",
        "module": "membros",
    },
    {
        "name": "gerar_relatorio_membros",
        "description": "Gera relatorio completo de membros. Parametros: tipo (resumo, completo, por_departamento)",
        "schema": {
            "type": "object",
            "properties": {
                "tipo": {"type": "string", "description": "Tipo de relatorio: resumo, completo, por_departamento"},
            },
            "required": ["tipo"],
        },
        "endpoint": "https://api.igreja.fbautomacao.space/api/membros/relatorio",
        "method": "GET",
        "module": "membros",
    },
    {
        "name": "criar_evento",
        "description": "Cria um novo evento na agenda da igreja. Parametros: titulo, descricao, data, hora, local, departamento_id, tipo",
        "schema": {
            "type": "object",
            "properties": {
                "titulo": {"type": "string", "description": "Titulo do evento"},
                "descricao": {"type": "string", "description": "Descricao detalhada"},
                "data": {"type": "string", "description": "Data do evento (YYYY-MM-DD)"},
                "hora": {"type": "string", "description": "Horario (HH:MM)"},
                "local": {"type": "string", "description": "Local do evento"},
                "departamento_id": {"type": "string", "description": "ID do departamento responsavel"},
                "tipo": {"type": "string", "description": "Tipo: culto, reuniao, especial, social"},
            },
            "required": ["titulo", "data"],
        },
        "endpoint": "https://api.igreja.fbautomacao.space/api/eventos",
        "method": "POST",
        "module": "eventos",
    },
    {
        "name": "listar_eventos",
        "description": "Lista eventos futuros ou por periodo. Parametros: data_inicio, data_fim, departamento_id, limite",
        "schema": {
            "type": "object",
            "properties": {
                "data_inicio": {"type": "string", "description": "Inicio do periodo (YYYY-MM-DD)"},
                "data_fim": {"type": "string", "description": "Fim do periodo (YYYY-MM-DD)"},
                "departamento_id": {"type": "string", "description": "Filtrar por departamento"},
                "limite": {"type": "integer", "description": "Maximo de resultados"},
            },
        },
        "endpoint": "https://api.igreja.fbautomacao.space/api/eventos",
        "method": "GET",
        "module": "eventos",
    },
    {
        "name": "consultar_agenda",
        "description": "Consulta a agenda do dia ou semana. Parametros: data, periodo (dia, semana, mes)",
        "schema": {
            "type": "object",
            "properties": {
                "data": {"type": "string", "description": "Data base (YYYY-MM-DD). Padrao: hoje"},
                "periodo": {"type": "string", "description": "Periodo: dia, semana, mes"},
            },
        },
        "endpoint": "https://api.igreja.fbautomacao.space/api/eventos/agenda",
        "method": "GET",
        "module": "eventos",
    },
    {
        "name": "consultar_entradas",
        "description": "Consulta entradas financeiras por periodo. Parametros: mes, ano, categoria",
        "schema": {
            "type": "object",
            "properties": {
                "mes": {"type": "integer", "description": "Mes (1-12)"},
                "ano": {"type": "integer", "description": "Ano"},
                "categoria": {"type": "string", "description": "Categoria: dízimo, oferta, doacao, evento"},
            },
        },
        "endpoint": "https://api.igreja.fbautomacao.space/api/financeiro/entradas",
        "method": "GET",
        "module": "financeiro",
    },
    {
        "name": "gerar_relatorio_financeiro",
        "description": "Gera relatorio financeiro completo. Parametros: mes_inicio, mes_fim, ano, tipo",
        "schema": {
            "type": "object",
            "properties": {
                "mes_inicio": {"type": "integer", "description": "Mes inicial"},
                "mes_fim": {"type": "integer", "description": "Mes final"},
                "ano": {"type": "integer", "description": "Ano"},
                "tipo": {"type": "string", "description": "Tipo: resumo, completo, por_categoria"},
            },
            "required": ["ano"],
        },
        "endpoint": "https://api.igreja.fbautomacao.space/api/financeiro/relatorio",
        "method": "GET",
        "module": "financeiro",
    },
]


async def seed():
    await init_db()
    async with async_session() as session:
        result = await session.execute(select(Tenant).where(Tenant.slug == "igreja"))
        tenant = result.scalar_one_or_none()
        if tenant:
            print(f"Tenant Igreja ja existe: {tenant.name} (key: {tenant.api_key})")
        else:
            api_key = f"kairos-{uuid.uuid4().hex[:24]}"
            tenant = Tenant(
                id=uuid.uuid4(),
                name="Igreja Cliente",
                slug="igreja",
                api_key=api_key,
                context=(
                    "Voce e o Kairos, assistente inteligente integrado ao sistema de gestao eclesiastica Kairos Igreja. "
                    "Você tem acesso aos modulos: Membros, Familias, Departamentos, Eventos, Financeiro e Relatorios. "
                    "Ajude o usuario com informacoes sobre membros, eventos, financas e relatorios da igreja. "
                    "Sempre responda de forma clara e amigavel em portugues do Brasil. "
                    "Quando o usuario perguntar sobre membros, use a ferramenta buscar_membro ou cadastrar_membro. "
                    "Para eventos, use criar_evento, listar_eventos ou consultar_agenda. "
                    "Para financas, use consultar_entradas ou gerar_relatorio_financeiro."
                ),
            )
            session.add(tenant)
            await session.commit()
            print(f"Tenant Igreja criado: {tenant.name}")
            print(f"API Key: {api_key}")

        app_result = await session.execute(
            select(App).where(App.tenant_id == tenant.id, App.slug == "igreja")
        )
        app = app_result.scalar_one_or_none()
        if app:
            print(f"App Kairos Igreja ja existe: {app.name}")
        else:
            app = App(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                name="Kairós Igreja",
                slug="igreja",
                origin_url="https://igreja.fbautomacao.space",
                context="Sistema de gestao eclesiastica com modulos: Membros, Familias, Departamentos, Eventos, Financeiro, Relatorios",
            )
            session.add(app)
            await session.commit()
            print(f"App Kairos Igreja criado: {app.name} (slug: {app.slug})")

        for tool_def in TOOLS_IGREJA:
            existing = await session.execute(
                select(Tool).where(Tool.app_id == app.id, Tool.name == tool_def["name"])
            )
            if existing.scalar_one_or_none():
                print(f"  Tool ja existe: {tool_def['name']}")
                continue

            tool = Tool(
                app_id=app.id,
                name=tool_def["name"],
                description=tool_def["description"],
                schema_json=json.dumps(tool_def["schema"]),
                endpoint=tool_def["endpoint"],
                method=tool_def["method"],
                headers_json=json.dumps({"Content-Type": "application/json"}),
                is_active=True,
            )
            session.add(tool)
            print(f"  Tool criada: {tool_def['name']} ({tool_def['module']})")

        await session.commit()
        print(f"\nResumo:")
        print(f"  Tenant: {tenant.name} (slug: {tenant.slug})")
        print(f"  App: {app.name} (slug: {app.slug})")
        print(f"  API Key: {tenant.api_key}")
        print(f"  Modulos: membros, familias, departamentos, eventos, financeiro, relatorios")
        print(f"  Tools registradas: {len(TOOLS_IGREJA)}")


if __name__ == "__main__":
    asyncio.run(seed())
