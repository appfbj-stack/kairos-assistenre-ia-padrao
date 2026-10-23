const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || ""

function headers() {
  return {
    Authorization: `Bearer ${API_KEY}`,
  }
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { headers: headers() })
  if (!res.ok) throw new Error(`${path} respondeu ${res.status}`)
  return res.json()
}

export type LangGraphAgent = {
  name: string
  status: string
  description: string
}

export type AgentStatus = {
  status: string
  langgraph_available: boolean
  agents: LangGraphAgent[]
  endpoints?: Record<string, string>
}

export type AionAgent = {
  id: string
  name: string
  description: string
  capabilities: string[]
}

export type InstalledApp = {
  id: string
  name: string
  slug: string
  version: string
  company: string
  environment: string
  status: string
  context: string
  api_url?: string
  origin_url?: string
  modules?: { name: string; description?: string; is_active?: boolean }[]
  permissions?: { key: string; name: string; module: string }[]
  tools?: any[]
}

export type RegisteredTool = {
  id: string
  name: string
  description?: string
  endpoint?: string
  method?: string
  is_active?: boolean
}

export type AuditLog = {
  id: string
  event_type: string
  tool_name?: string
  app_slug?: string
  user_name?: string
  user_role?: string
  success: boolean
  result?: string
  created_at: string
}

export type Conversation = {
  id: string
  title: string
  created_at: string | null
  updated_at: string | null
}

export const getAgentStatus = () => get<AgentStatus>("/api/agents/status")
export const getAionAgents = () => get<{ agents: AionAgent[] }>("/api/aion/agents")
export const getInstalledApps = () =>
  get<{ apps: InstalledApp[]; total?: number }>("/api/apps")
export const getTools = () => get<{ tools: RegisteredTool[] }>("/api/tools/list")
export const getAuditLogs = () =>
  get<{ logs: AuditLog[]; total: number; limit?: number; offset?: number }>(
    "/api/audit/logs"
  )
export const getConversations = () =>
  get<{ conversations: Conversation[]; total: number }>("/api/conversations")

export function formatDate(value?: string | null): string {
  if (!value) return "-"
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return "-"
  return d.toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}
