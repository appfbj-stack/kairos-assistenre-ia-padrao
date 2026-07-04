# App Registry — Manual de Implementação

## Visão Geral

O **App Registry** é o sistema central de registro automático de aplicativos no ecossistema Kairós.
Cada aplicativo que deseja usar o Kairós como motor de IA deve se registrar fornecendo metadados,
módulos, permissões, ferramentas e recursos suportados.

## Arquitetura

O módulo segue **Clean Architecture** com 4 camadas:

```
Domain (core/domain/entities/app.py)
  └── Port (core/domain/interfaces/app_port.py)
       └── Application (core/application/app_registry.py)
            └── Infrastructure (backend/app/repos/app_repo.py)
                 └── Interface (backend/app/routes/apps.py)
```

### Fluxo de Registro

1. Aplicativo envia `POST /api/apps/register` com API Key do tenant
2. `resolve_tenant` valida a chave e identifica o tenant
3. `AppRegistry.register()` valida slug, versão, nome e tenant
4. `AppRepo` persiste no banco (tabela `apps` expandida)
5. Retorna o AppDef completo com ID, timestamps

### Registro Automático na Inicialização

No startup (`lifespan` em `main.py`), o sistema:

1. Lista todos os tenants ativos
2. Para cada tenant, verifica se já existe "Kairós Igreja" registrado
3. Se não existir, cria o registro automaticamente com módulos, permissões e recursos

## Modelo de Dados

### App (tabela `apps`)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | PK auto-gerado |
| tenant_id | UUID | FK para o tenant |
| name | VARCHAR(255) | Nome do app |
| slug | VARCHAR(100) | Slug único por tenant |
| version | VARCHAR(20) | Versão semântica (ex: 2.0.0) |
| company | VARCHAR(255) | Empresa desenvolvedora |
| api_url | VARCHAR(500) | URL base da API do app |
| environment | VARCHAR(20) | development, staging, production |
| icon | VARCHAR(50) | Nome do ícone (Lucide) |
| primary_color | VARCHAR(7) | Cor primária em hex (ex: #1e40af) |
| status | VARCHAR(20) | active, inactive, maintenance |
| origin_url | VARCHAR(500) | URL de origem do app |
| context | TEXT | Contexto para o sistema |
| modules | JSON | Lista de módulos [{name, description, is_active}] |
| permissions | JSON | Lista de permissões [{key, name, description, module}] |
| supported_resources | JSON | Recursos: voice, image, document, agent |
| is_active | BOOLEAN | Se o app está ativo |
| created_at | TIMESTAMP | Data de criação |
| updated_at | TIMESTAMP | Data da última atualização |

## API Endpoints

### `POST /api/apps/register`
Registra um novo aplicativo.

**Headers:** `Authorization: Bearer <api_key>`

**Body:**
```json
{
  "name": "Meu App",
  "slug": "meu-app",
  "version": "1.0.0",
  "company": "Minha Empresa",
  "api_url": "https://api.meuapp.com",
  "environment": "production",
  "icon": "Church",
  "primary_color": "#1e40af",
  "origin_url": "https://meuapp.com",
  "context": "Descrição do contexto do app",
  "modules": [
    {"name": "vendas", "description": "Gestão de vendas", "is_active": true}
  ],
  "permissions": [
    {"key": "vendas.view", "name": "Ver vendas", "module": "vendas"}
  ],
  "supported_resources": ["voice", "image", "document", "agent"]
}
```

### `PUT /api/apps/{id}`
Atualiza informações do app. Apenas campos fornecidos são alterados.

### `DELETE /api/apps/{id}`
Remove o app e suas ferramentas associadas.

### `GET /api/apps/{id}`
Retorna detalhes do app.

### `GET /api/apps/slug/{slug}`
Busca app por slug (dentro do tenant autenticado).

### `GET /api/apps`
Lista todos os apps do tenant autenticado.

### `PATCH /api/apps/{id}/status?status=active`
Altera o status do app (active, inactive, maintenance).

### `POST /api/apps/context`
Registra contexto do app no gerenciador de contexto.

### `POST /api/apps/session`
Registra sessão de usuário do app.

## SDK JavaScript

### Inicialização com auto-registro

```javascript
// Inicializar
const client = Kairos.initialize({
  apiUrl: "https://api.assistente.fbautomacao.space",
  apiKey: "tenant-api-key",
  appSlug: "meu-app",
  appName: "Meu App",
  appVersion: "1.0.0",
  company: "Minha Empresa",
  environment: "production",
  icon: "Church",
  primaryColor: "#1e40af",
})

// Auto-registro (opcional - registra se não existir)
const app = await Kairos.autoRegister({
  modules: [{ name: "vendas", description: "Gestão de vendas" }],
  permissions: [{ key: "vendas.view", name: "Ver vendas", module: "vendas" }],
  supportedResources: ["voice", "image", "document"],
})
```

### Métodos do App Registry

```javascript
// CRUD completo
await client.registerApp(name, slug, options)
await client.getApp(appId)
await client.getAppBySlug(slug)
await client.listApps()
await client.updateApp(appId, data)
await client.removeApp(appId)
await client.setAppStatus(appId, "active")

// Contexto e Sessão
await client.registerContext(appName, modules, context)
await client.registerSession(userId, userName, userEmail, userRole, modules, departments)
```

## Python SDK

```python
from core.sdk import KairosSDK

sdk = await KairosSDK.build(...)

# Registrar app
from core.domain.entities.app import AppDef, AppModule, AppPermission
app = AppDef(
    id="",
    tenant_id="tenant-uuid",
    name="Meu App",
    slug="meu-app",
    version="1.0.0",
    company="Minha Empresa",
    modules=[AppModule(name="vendas", description="Gestão de vendas")],
    permissions=[AppPermission(key="vendas.view", name="Ver vendas", module="vendas")],
)
result = await sdk.register_app(app)

# Listar apps
apps = await sdk.list_apps(tenant_id)
```

## Validações

- **Slug:** Apenas letras minúsculas, números, hífens e underscores (3-50 caracteres)
- **Versão:** Formato semântico `x.y.z` (obrigatório)
- **Nome:** Não pode ser vazio
- **Tenant ID:** Obrigatório
- **Dados duplicados:** Slug único por tenant
- **Status:** Apenas `active`, `inactive`, `maintenance`

## Testando

```bash
# 1. Registrar um app
curl -X POST http://localhost:8070/api/apps/register \
  -H "Authorization: Bearer kairos-b4cad9a30caf4491809f90ff" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Teste App",
    "slug": "teste-app",
    "version": "1.0.0",
    "company": "Teste Ltda",
    "modules": [{"name": "testes", "description": "Módulo de teste"}],
    "permissions": [{"key": "teste.view", "name": "Ver testes", "module": "testes"}]
  }'

# 2. Listar apps
curl -H "Authorization: Bearer kairos-b4cad9a30caf4491809f90ff" \
  http://localhost:8070/api/apps

# 3. Buscar por slug
curl -H "Authorization: Bearer kairos-b4cad9a30caf4491809f90ff" \
  http://localhost:8070/api/apps/slug/teste-app

# 4. Atualizar app
curl -X PUT http://localhost:8070/api/apps/<id> \
  -H "Authorization: Bearer kairos-b4cad9a30caf4491809f90ff" \
  -H "Content-Type: application/json" \
  -d '{"version": "2.0.0", "company": "Teste S.A."}'

# 5. Mudar status
curl -X PATCH "http://localhost:8070/api/apps/<id>/status?status=maintenance" \
  -H "Authorization: Bearer kairos-b4cad9a30caf4491809f90ff"

# 6. Remover app
curl -X DELETE http://localhost:8070/api/apps/<id> \
  -H "Authorization: Bearer kairos-b4cad9a30caf4491809f90ff"
```
