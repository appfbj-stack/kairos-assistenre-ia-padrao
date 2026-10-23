"use client"

import { useEffect, useState } from "react"
import {
  Bot,
  CheckCircle,
  Cpu,
  RefreshCw,
  AlertTriangle,
  UserCheck,
  Activity,
} from "lucide-react"
import * as api from "@/lib/assistantApi"
import { Button } from "@/components/ui/button"

export default function AgentesPage() {
  const [status, setStatus] = useState<api.AgentStatus | null>(null)
  const [aionAgents, setAionAgents] = useState<api.AionAgent[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const [s, a] = await Promise.all([api.getAgentStatus(), api.getAionAgents()])
      setStatus(s)
      setAionAgents(Array.isArray(a.agents) ? a.agents : [])
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao carregar agentes")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const langGraphAgents = status?.agents ?? []

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-blue-500/30 flex items-center justify-center">
            <Bot className="w-6 h-6 text-blue-400" />
          </div>
          <div>
            <h1 className="text-xl font-semibold">Agentes</h1>
            <p className="text-sm text-muted-foreground">
              Agentes especializados e agentes defusores
            </p>
          </div>
        </div>
        <Button variant="outline" size="sm" onClick={load} disabled={loading}>
          <RefreshCw className={`w-4 h-4 mr-1 ${loading ? "animate-spin" : ""}`} />
          Atualizar
        </Button>
      </div>

      {error && (
        <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-destructive/10 border border-destructive/30 text-sm text-destructive">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}

      <div className="grid grid-cols-2 sm:grid-cols4 gap-4">
        <div className="glass-card rounded-xl p-4 space-y-1">
          <p className="text-xs text-muted-foreground">Motor</p>
          <div className="flex items-center gap-2">
            {status?.langgraph_available ? (
              <CheckCircle className="w-4 h-4 text-green-500" />
            ) : (
              <AlertTriangle className="w-4 h-4 text-amber-500" />
            )}
            <span className="text-sm font-medium capitalize">
              {status?.status ?? "-"}
            </span>
          </div>
        </div>
        <div className="glass-card rounded-xl p-4 space-y-1">
          <p className="text-xs text-muted-foreground">Agentes LangGraph</p>
          <p className="text-lg font-semibold">{langGraphAgents.length}</p>
        </div>
        <div className="glass-card rounded-xl p-4 space-y-1">
          <p className="text-xs text-muted-foreground">Agentes Aion</p>
          <p className="text-lg font-semibold">{aionAgents.length}</p>
        </div>
        <div className="glass-card rounded-xl p-4 space-y-1">
          <p className="text-xs text-muted-foreground">Ativos</p>
          <p className="text-lg font-semibold">
            {langGraphAgents.filter((a) => a.status === "active").length}
          </p>
        </div>
      </div>

      <div className="glass-card rounded-xl p-6 space-y-4">
        <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
          Agentes de execução
        </h2>
        {langGraphAgents.length === 0 && !loading && (
          <p className="text-sm text-muted-foreground text-center py-6">
            Nenhum agente registrado.
          </p>
        )}
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {langGraphAgents.map((agent) => (
            <div
              key={agent.name}
              className="flex items-start gap-3 p-3 rounded-lg bg-accent/30 border border-glass-border"
            >
              <div className="shrink-0 w-9 h-9 rounded-lg bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-blue-500/30 flex items-center justify-center">
                <Activity className="w-4 h-4 text-blue-400" />
              </div>
              <div className="min-w-0">
                <p className="text-sm font-medium capitalize">{agent.name}</p>
                <p className="text-xs text-muted-foreground">{agent.description}</p>
                <span
                  className={`inline-block mt-1.5 text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full ${
                    agent.status === "active"
                      ? "text-green-500 bg-green-500/10"
                      : "text-amber-500 bg-amber-500/10"
                  }`}
                >
                  {agent.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="glass-card rounded-xl p-6 space-y-4">
        <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
          Agentes de domínio
        </h2>
        {aionAgents.length === 0 && !loading && (
          <p className="text-sm text-muted-foreground text-center py-6">
            Nenhum agente de domínio registrado.
          </p>
        )}
        <div className="grid gap-3 sm:grid-cols-2">
          {aionAgents.map((agent) => (
            <div
              key={agent.id}
              className="glass-card rounded-xl p-4 space-y-3"
            >
              <div className="flex items-start gap-3">
                <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-purple-500/20 to-blue-500/20 border border-purple-500/30 flex items-center justify-center shrink-0">
                  <UserCheck className="w-4 h-4 text-purple-400" />
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-medium">{agent.name}</p>
                  <p className="text-xs text-muted-foreground">{agent.description}</p>
                </div>
              </div>
              {agent.capabilities && agent.capabilities.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {agent.capabilities.map((cap, i) => (
                    <span
                      key={i}
                      className="text-xs bg-accent/50 text-muted-foreground px-2 py-0.5 rounded-full"
                    >
                      {cap}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {status?.endpoints && Object.keys(status.endpoints).length > 0 && (
        <div className="glass-card rounded-xl p-6 space-y-3">
          <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
            Endpoints
          </h2>
          <div className="space-y-1.5">
            {Object.entries(status.endpoints).map(([k, v]) => (
              <div key={k} className="flex items-center gap-3 text-xs">
                <span className="text-muted-foreground capitalize w-32 shrink-0">
                  {k.replace(/_/g, " ")}
                </span>
                <code className="bg-accent/50 px-2 py-1 rounded text-foreground">
                  {v}
                </code>
              </div>
            ))}
          </div>
        </div>
      )}

      <p className="text-xs text-muted-foreground flex items-center gap-2">
        <Cpu className="w-3.5 h-3.5" />
        Fonte: /api/agents/status e /api/aion/agents
      </p>
    </div>
  )
}
