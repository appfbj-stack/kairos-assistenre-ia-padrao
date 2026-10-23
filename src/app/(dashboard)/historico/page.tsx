"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { History, RefreshCw, AlertTriangle, MessageSquare, ArrowRight } from "lucide-react"
import * as api from "@/lib/assistantApi"
import { Button } from "@/components/ui/button"

export default function HistoricoPage() {
  const [conversations, setConversations] = useState<api.Conversation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.getConversations()
      setConversations(Array.isArray(res.conversations) ? res.conversations : [])
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao carregar o histórico")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-slate-500/20 to-blue-500/20 border border-blue-500/30 flex items-center justify-center">
            <History className="w-6 h-6 text-blue-400" />
          </div>
          <div>
            <h1 className="text-xl font-semibold">Histórico</h1>
            <p className="text-sm text-muted-foreground">
              Conversas registradas nesta conta
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

      <div className="glass-card rounded-xl p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
            Conversas
          </h2>
          <span className="text-xs text-muted-foreground bg-accent/50 px-2 py-0.5 rounded-full">
            {conversations.length}
          </span>
        </div>

        {conversations.length === 0 && !loading && (
          <div className="text-center py-10 space-y-2">
            <MessageSquare className="w-8 h-8 text-muted-foreground/50 mx-auto" />
            <p className="text-sm font-medium">Nenhuma conversa ainda</p>
            <p className="text-xs text-muted-foreground">
              As conversas que você iniciar aparecem aqui.
            </p>
            <Link
              href="/chat"
              className="inline-flex items-center gap-1.5 text-xs text-primary hover:underline mt-2"
            >
              Ir para Conversas
              <ArrowRight className="w-3 h-3" />
            </Link>
          </div>
        )}

        <div className="space-y-2">
          {conversations.map((c) => (
            <div
              key={c.id}
              className="flex items-center justify-between gap-3 p-3 rounded-lg bg-accent/30 border border-glass-border"
            >
              <div className="min-w-0">
                <p className="text-sm font-medium truncate">{c.title}</p>
                <p className="text-xs text-muted-foreground">
                  Atualizada em {api.formatDate(c.updated_at)}
                </p>
              </div>
              <MessageSquare className="w-4 h-4 text-muted-foreground shrink-0" />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
