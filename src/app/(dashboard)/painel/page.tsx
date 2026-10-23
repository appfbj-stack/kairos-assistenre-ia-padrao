"use client"

import { useEffect, useState } from "react"
import {
  BarChart2,
  CheckCircle,
  RefreshCw,
  AlertTriangle,
  Package,
  Puzzle,
  ScrollText,
  XCircle,
} from "lucide-react"
import * as api from "@/lib/assistantApi"
import { Button } from "@/components/ui/button"

export default function PainelPage() {
  const [apps, setApps] = useState<api.InstalledApp[]>([])
  const [tools, setTools] = useState<api.RegisteredTool[]>([])
  const [logs, setLogs] = useState<api.AuditLog[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const [a, t, l] = await Promise.all([
        api.getInstalledApps(),
        api.getTools(),
        api.getAuditLogs(),
      ])
      setApps(Array.isArray(a.apps) ? a.apps : [])
      setTools(Array.isArray(t.tools) ? t.tools : [])
      setLogs(Array.isArray(l.logs) ? l.logs : [])
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao carregar o painel")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const totalModules = apps.reduce(
    (acc, a) => acc + (a.modules?.filter((m) => m.is_active !== false).length ?? 0),
    0
  )
  const totalPermissions = apps.reduce(
    (acc, a) => acc + (a.permissions?.length ?? 0),
    0
  )
  const activeApps = apps.filter((a) => a.status === "active").length

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-amber-500/20 to-orange-500/20 border border-amber-500/30 flex items-center justify-center">
            <BarChart2 className="w-6 h-6 text-amber-400" />
          </div>
          <div>
            <h1 className="text-xl font-semibold">Painel</h1>
            <p className="text-sm text-muted-foreground">
              Apps instalados, módulos e trilha de auditoria
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

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="glass-card rounded-xl p-4 space-y-1">
          <p className="text-xs text-muted-foreground">Apps instalados</p>
          <p className="text-lg font-semibold">{apps.length}</p>
        </div>
        <div className="glass-card rounded-xl p-4 space-y-1">
          <p className="text-xs text-muted-foreground">Apps ativos</p>
          <p className="text-lg font-semibold text-green-500">{activeApps}</p>
        </div>
        <div className="glass-card rounded-xl p-4 space-y-1">
          <p className="text-xs text-muted-foreground">Módulos</p>
          <p className="text-lg font-semibold">{totalModules}</p>
        </div>
        <div className="glass-card rounded-xl p-4 space-y-1">
          <p className="text-xs text-muted-foreground">Permissões</p>
          <p className="text-lg font-semibold">{totalPermissions}</p>
        </div>
      </div>

      <div className="glass-card rounded-xl p-6 space-y-4">
        <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
          Apps
        </h2>
        {apps.length === 0 && !loading && (
          <p className="text-sm text-muted-foreground text-center py-6">
            Nenhum app registrado.
          </p>
        )}
        <div className="space-y-3">
          {apps.map((app) => (
            <div key={app.id} className="glass-card rounded-xl p-4 space-y-3">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <Package className="w-4 h-4 text-blue-400 shrink-0" />
                    <p className="text-sm font-medium truncate">{app.name}</p>
                    <span className="text-[10px] uppercase tracking-wider text-muted-foreground bg-accent/50 px-1.5 py-0.5 rounded">
                      v{app.version}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-0.5">{app.context}</p>
                </div>
                <span
                  className={`text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full shrink-0 ${
                    app.status === "active"
                      ? "text-green-500 bg-green-500/10"
                      : "text-amber-500 bg-amber-500/10"
                  }`}
                >
                  {app.status}
                </span>
              </div>

              {app.modules && app.modules.length > 0 && (
                <div className="space-y-1.5">
                  <p className="text-[10px] uppercase tracking-wider text-muted-foreground">
                    Módulos
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {app.modules.map((m) => (
                      <span
                        key={m.name}
                        className={`text-xs px-2 py-0.5 rounded-full ${
                          m.is_active === false
                            ? "bg-accent/30 text-muted-foreground/60"
                            : "bg-primary/10 text-primary"
                        }`}
                      >
                        {m.name}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {app.permissions && app.permissions.length > 0 && (
                <div className="space-y-1.5">
                  <p className="text-[10px] uppercase tracking-wider text-muted-foreground">
                    Permissões
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {app.permissions.map((p) => (
                      <span
                        key={p.key}
                        className="text-xs bg-accent/50 text-muted-foreground px-2 py-0.5 rounded-full"
                      >
                        {p.name}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="glass-card rounded-xl p-6 space-y-4">
        <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
          Ferramentas registradas
        </h2>
        {tools.length === 0 && !loading && (
          <p className="text-sm text-muted-foreground text-center py-6">
            Nenhuma ferramenta registrada.
          </p>
        )}
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {tools.map((tool) => (
            <div
              key={tool.id}
              className="flex items-start gap-3 p-3 rounded-lg bg-accent/30 border border-glass-border"
            >
              <Puzzle className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" />
              <div className="min-w-0">
                <p className="text-sm font-medium truncate">{tool.name}</p>
                <p className="text-xs text-muted-foreground truncate">
                  {tool.description}
                </p>
                {tool.endpoint && (
                  <code className="text-[10px] bg-accent/50 px-1.5 py-0.5 rounded mt-1 inline-block">
                    {tool.method ?? "POST"} {tool.endpoint}
                  </code>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="glass-card rounded-xl p-6 space-y-4">
        <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
          Auditoria
        </h2>
        {logs.length === 0 && !loading && (
          <div className="text-center py-6 space-y-2">
            <CheckCircle className="w-8 h-8 text-green-500 mx-auto" />
            <p className="text-sm font-medium">Nenhum evento registrado</p>
            <p className="text-xs text-muted-foreground">
              As ações do assistente aparecem aqui.
            </p>
          </div>
        )}
        {logs.length > 0 && (
          <div className="space-y-2">
            {logs.map((log) => (
              <div
                key={log.id}
                className="flex items-start justify-between gap-3 p-3 rounded-lg bg-accent/30 border border-glass-border"
              >
                <div className="flex items-start gap-3 min-w-0">
                  <ScrollText className="w-4 h-4 text-muted-foreground shrink-0 mt-0.5" />
                  <div className="min-w-0">
                    <p className="text-sm font-medium">{log.event_type}</p>
                    <p className="text-xs text-muted-foreground">
                      {log.tool_name ? `${log.tool_name} · ` : ""}
                      {log.user_name ?? "sistema"} ·{" "}
                      {api.formatDate(log.created_at)}
                    </p>
                  </div>
                </div>
                {log.success ? (
                  <CheckCircle className="w-4 h-4 text-green-500 shrink-0" />
                ) : (
                  <XCircle className="w-4 h-4 text-red-500 shrink-0" />
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
