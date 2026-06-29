"use client"

import { useEffect, useState } from "react"
import {
  Cpu,
  Zap,
  Wifi,
  WifiOff,
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertTriangle,
  UserCheck,
  RotateCcw,
} from "lucide-react"
import { useAionStore } from "@/stores/aionStore"
import * as aionApi from "@/lib/aionApi"
import { Button } from "@/components/ui/button"

type Tab = "overview" | "skills" | "mcps" | "agents" | "approvals"

export default function AionPage() {
  const {
    connected, initialized, loading, error,
    skills, mcps, agents, pendingApprovals,
    setConnected, setInitialized, setLoading, setError,
    setSkills, setMcps, setAgents, setPendingApprovals,
    updateSkillActive,
  } = useAionStore()

  const [tab, setTab] = useState<Tab>("overview")

  const loadAll = async () => {
    setLoading(true)
    setError(null)
    try {
      const [status, s, m, a, ap] = await Promise.all([
        aionApi.getAionStatus(),
        aionApi.getAionSkills(),
        aionApi.getAionMcps(),
        aionApi.getAionAgents(),
        aionApi.getPendingApprovals(),
      ])
      setConnected(status.connected ?? false)
      setInitialized(status.initialized ?? false)
      setSkills(Array.isArray(s.skills) ? s.skills : [])
      setMcps(Array.isArray(m.mcps) ? m.mcps : [])
      setAgents(Array.isArray(a.agents) ? a.agents : [])
      setPendingApprovals(Array.isArray(ap.approvals) ? ap.approvals : [])
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao carregar Aion")
    } finally {
      setLoading(false)
    }
  }

  const handleInit = async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await aionApi.initializeAion()
      setConnected(result.connected ?? true)
      setInitialized(true)
      await loadAll()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao inicializar")
    } finally {
      setLoading(false)
    }
  }

  const handleToggleSkill = async (name: string, currentActive: boolean) => {
    updateSkillActive(name, !currentActive)
    try {
      await aionApi.toggleSkill(name)
    } catch {
      updateSkillActive(name, currentActive)
    }
  }

  const handleApproval = async (id: string, decision: "approve" | "reject") => {
    try {
      await aionApi.approveAction(id, decision)
      await loadAll()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro na aprovação")
    }
  }

  useEffect(() => {
    loadAll()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const tabs: { key: Tab; label: string; badge?: number }[] = [
    { key: "overview", label: "Visão Geral" },
    { key: "skills", label: "Skills", badge: skills.length },
    { key: "mcps", label: "MCPs", badge: mcps.length },
    { key: "agents", label: "Agentes", badge: agents.length },
    { key: "approvals", label: "Aprovações", badge: pendingApprovals.length },
  ]

  const activeSkills = skills.filter((s) => s.is_active).length

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-purple-500/20 to-blue-500/20 border border-purple-500/30 flex items-center justify-center">
            <Cpu className="w-6 h-6 text-purple-400" />
          </div>
          <div>
            <h1 className="text-xl font-semibold">Aion Engine</h1>
            <p className="text-sm text-muted-foreground">
              Motor interno de Skills, MCPs e Agentes
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {!initialized && (
            <Button onClick={handleInit} disabled={loading} size="sm">
              <Zap className="w-4 h-4 mr-1" />
              Inicializar
            </Button>
          )}
          <Button
            variant="outline"
            size="sm"
            onClick={loadAll}
            disabled={loading}
          >
            <RefreshCw className={`w-4 h-4 mr-1 ${loading ? "animate-spin" : ""}`} />
            Atualizar
          </Button>
        </div>
      </div>

      {/* Connection Banner */}
      {error && (
        <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-destructive/10 border border-destructive/30 text-sm text-destructive">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}

      {!connected && initialized && (
        <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-sm text-amber-600 dark:text-amber-400">
          <WifiOff className="w-4 h-4 shrink-0" />
          Aion runtime não está disponível. Os dados abaixo são de demonstração.
        </div>
      )}

      {/* Status Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="glass-card rounded-xl p-4 space-y-1">
          <p className="text-xs text-muted-foreground">Status</p>
          <div className="flex items-center gap-2">
            {connected ? (
              <Wifi className="w-4 h-4 text-green-500" />
            ) : initialized ? (
              <WifiOff className="w-4 h-4 text-amber-500" />
            ) : (
              <XCircle className="w-4 h-4 text-muted-foreground" />
            )}
            <span className="text-sm font-medium">
              {connected ? "Conectado" : initialized ? "Demo" : "Offline"}
            </span>
          </div>
        </div>
        <div className="glass-card rounded-xl p-4 space-y-1">
          <p className="text-xs text-muted-foreground">Skills</p>
          <p className="text-lg font-semibold">
            {activeSkills}/{skills.length}
          </p>
        </div>
        <div className="glass-card rounded-xl p-4 space-y-1">
          <p className="text-xs text-muted-foreground">MCPs</p>
          <p className="text-lg font-semibold">{mcps.length}</p>
        </div>
        <div className="glass-card rounded-xl p-4 space-y-1">
          <p className="text-xs text-muted-foreground">Aprovações</p>
          <p className="text-lg font-semibold">
            {pendingApprovals.length > 0 ? (
              <span className="text-amber-500">{pendingApprovals.length}</span>
            ) : (
              0
            )}
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-glass-border pb-1 overflow-x-auto">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-2 text-sm rounded-lg transition-colors whitespace-nowrap ${
              tab === t.key
                ? "bg-primary/10 text-primary font-medium"
                : "text-muted-foreground hover:text-foreground hover:bg-accent/50"
            }`}
          >
            {t.label}
            {t.badge !== undefined && t.badge > 0 && (
              <span className="ml-2 text-xs bg-primary/20 text-primary px-1.5 py-0.5 rounded-full">
                {t.badge}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="space-y-4">
        {tab === "overview" && (
          <div className="glass-card rounded-xl p-6 space-y-4">
            <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
              Capacidades Disponíveis
            </h2>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {[...skills, ...mcps.map((m) => ({ ...m, type: "mcp" as const }))].map((cap, i) => (
                <div
                  key={i}
                  className="flex items-start gap-3 p-3 rounded-lg bg-accent/30 border border-glass-border"
                >
                  <div className="shrink-0">
                    {"is_active" in cap && cap.is_active !== undefined ? (
                      <CheckCircle className="w-4 h-4 text-green-500" />
                    ) : (
                      <CheckCircle className="w-4 h-4 text-muted-foreground/50" />
                    )}
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate">{cap.name}</p>
                    <p className="text-xs text-muted-foreground truncate">
                      {cap.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {tab === "skills" && (
          <div className="space-y-3">
            {skills.length === 0 && (
              <p className="text-sm text-muted-foreground text-center py-8">
                Nenhuma skill registrada.
              </p>
            )}
            {skills.map((skill) => (
              <div
                key={skill.id}
                className="glass-card rounded-xl p-4 flex items-center justify-between"
              >
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium">{skill.name}</p>
                    <span className="text-[10px] uppercase tracking-wider text-muted-foreground bg-accent/50 px-1.5 py-0.5 rounded">
                      {skill.category}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    {skill.description}
                  </p>
                </div>
                <Button
                  variant={skill.is_active ? "default" : "outline"}
                  size="sm"
                  onClick={() => handleToggleSkill(skill.name, skill.is_active)}
                >
                  {skill.is_active ? "Ativo" : "Inativo"}
                </Button>
              </div>
            ))}
          </div>
        )}

        {tab === "mcps" && (
          <div className="space-y-3">
            {mcps.length === 0 && (
              <p className="text-sm text-muted-foreground text-center py-8">
                Nenhum MCP registrado.
              </p>
            )}
            {mcps.map((mcp) => (
              <div
                key={mcp.id}
                className="glass-card rounded-xl p-4 space-y-3"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium">{mcp.name}</p>
                    <p className="text-xs text-muted-foreground">{mcp.description}</p>
                  </div>
                  <code className="text-[10px] bg-accent/50 px-2 py-1 rounded">
                    {mcp.endpoint}
                  </code>
                </div>
                {mcp.tools.length > 0 && (
                  <div className="flex flex-wrap gap-1.5">
                    {mcp.tools.map((tool, i) => (
                      <span
                        key={i}
                        className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full"
                      >
                        {tool.name}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {tab === "agents" && (
          <div className="grid gap-3 sm:grid-cols-2">
            {agents.length === 0 && (
              <p className="text-sm text-muted-foreground text-center py-8 col-span-full">
                Nenhum agente registrado.
              </p>
            )}
            {agents.map((agent) => (
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
                {agent.capabilities.length > 0 && (
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
        )}

        {tab === "approvals" && (
          <div className="space-y-3">
            {pendingApprovals.length === 0 && (
              <div className="glass-card rounded-xl p-8 text-center space-y-2">
                <CheckCircle className="w-8 h-8 text-green-500 mx-auto" />
                <p className="text-sm font-medium">Nenhuma aprovação pendente</p>
                <p className="text-xs text-muted-foreground">
                  Todas as ações foram processadas.
                </p>
              </div>
            )}
            {pendingApprovals.map((app) => (
              <div key={app.id} className="glass-card rounded-xl p-4 space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium capitalize">{app.action.replace(/_/g, " ")}</p>
                    <p className="text-xs text-muted-foreground">
                      {app.action_type} &middot; {app.requested_by}
                    </p>
                  </div>
                  <span className="text-[10px] uppercase tracking-wider text-amber-500 bg-amber-500/10 px-2 py-0.5 rounded-full">
                    Pendente
                  </span>
                </div>
                {Object.keys(app.details).length > 0 && (
                  <div className="bg-accent/30 rounded-lg p-3 space-y-1">
                    {Object.entries(app.details).map(([k, v]) => (
                      <div key={k} className="flex gap-2 text-xs">
                        <span className="text-muted-foreground capitalize">{k}:</span>
                        <span className="text-foreground truncate">
                          {typeof v === "object" ? JSON.stringify(v) : String(v)}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    className="flex-1"
                    onClick={() => handleApproval(app.id, "approve")}
                  >
                    <CheckCircle className="w-3.5 h-3.5 mr-1" />
                    Aprovar
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="flex-1"
                    onClick={() => handleApproval(app.id, "reject")}
                  >
                    <RotateCcw className="w-3.5 h-3.5 mr-1" />
                    Rejeitar
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
