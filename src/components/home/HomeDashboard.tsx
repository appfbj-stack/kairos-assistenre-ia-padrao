"use client"

import { useRouter } from "next/navigation"
import { useState } from "react"
import {
    Search, Bell, MoreVertical,
    CheckSquare, Database, Users, Zap,
    Mic, Send, Plus, Grid3X3,
    MessageSquare, FileText, Image, Terminal, Volume2,
    Activity, Check, Loader, Church, Wrench, LayoutGrid, DollarSign,
    Star, BarChart2, Table, HardDrive, ArrowRight,
    Globe, Keyboard,
} from "lucide-react"

const statCards = [
  { icon: CheckSquare, value: "3", label: "Tarefas pendentes", color: "#60a5fa" },
  { icon: Database, value: "2", label: "Backups realizados", color: "#60a5fa" },
  { icon: Users, value: "5", label: "Aniversariantes hoje", color: "#60a5fa" },
  { icon: Zap, value: "100%", label: "Sistemas ativos", color: "#facc15", bg: "rgba(234,179,8,0.08)" },
  ]

const actionCards = [
  {
        icon: MessageSquare,
        title: "Conversar",
        desc: "Bate-papo inteligente",
        color: "#60a5fa",
        bg: "rgba(59,130,246,0.12)",
        href: "/chat",
  },
  {
        icon: FileText,
        title: "Analisar documento",
        desc: "Leia e extraia informaÃ§Ãµes",
        color: "#34d399",
        bg: "rgba(16,185,129,0.12)",
        titleColor: "#34d399",
        href: "/documentos",
  },
  {
        icon: Image,
        title: "Analisar imagem",
        desc: "Entenda o que vocÃª vÃª",
        color: "#c084fc",
        bg: "rgba(139,92,246,0.12)",
        href: "/documentos",
  },
  {
        icon: Zap,
        title: "Executar tarefa",
        desc: "Automatize processos",
        color: "#facc15",
        bg: "rgba(234,179,8,0.12)",
        titleColor: "#facc15",
        href: "/ferramentas",
  },
  {
        icon: Volume2,
        title: "Falar",
        desc: "Converse por voz com KairÃ³s",
        color: "#60a5fa",
        bg: "rgba(59,130,246,0.08)",
        href: "/chat",
  },
  ]

const recentActivity = [
  { icon: Church, title: "Cadastrar novo membro", sub: "Sistema Igreja", time: "09:45", status: "done", color: "#60a5fa" },
  { icon: Wrench, title: "OrÃ§amento de serviÃ§o", sub: "Sistema Oficina", time: "09:30", status: "done", color: "#94a3b8" },
  { icon: FileText, title: "AnÃ¡lise de PDF", sub: "Documento: RelatÃ³rio_abril.pdf", time: "09:15", status: "done", color: "#60a5fa" },
  { icon: LayoutGrid, title: "Organizar pasta Downloads", sub: "AÃ§Ã£o no computador", time: "08:50", status: "done", color: "#facc15" },
  { icon: BarChart2, title: "RelatÃ³rio financeiro", sub: "Sistema Financeiro", time: "08:30", status: "loading", color: "#60a5fa" },
  { icon: Database, title: "Backup completo", sub: "Todos os sistemas", time: "Ontem", status: "done", color: "#60a5fa" },
  ]

const connectedSystems = [
  { icon: Church, name: "Igreja", online: true },
  { icon: Wrench, name: "Oficina", online: true },
  { icon: LayoutGrid, name: "VidraÃ§aria", online: true },
  { icon: DollarSign, name: "Financeiro", online: true },
  ]

const suggestions = [
  { icon: BarChart2, title: "Gerar relatÃ³rio mensal", sub: "Financeiro", color: "#60a5fa" },
  { icon: Table, title: "Importar dados do Excel", sub: "Membros", color: "#34d399" },
  { icon: Database, title: "Fazer backup agora", sub: "Proteja seus dados", color: "#60a5fa" },
  ]

export function HomeDashboard() {
    const router = useRouter()
    const [input, setInput] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        if (!input.trim()) return
        router.push(`/chat?q=${encodeURIComponent(input.trim())}`)
  }

  return (
        <div className="flex flex-col h-full overflow-hidden" style={{ background: "#07071a" }}>
          {/* TOP HEADER */}
                <div className="flex items-center justify-between px-8 py-4 shrink-0" style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                          <div />
                          <div className="flex items-center gap-4">
                                    <button className="p-2 rounded-xl transition-all hover:bg-white/[0.05]" style={{ color: "#475569" }}>
                                                <Search className="w-5 h-5" />
                                    </button>
                                    <div className="relative">
                                                <button className="p-2 rounded-xl transition-all hover:bg-white/[0.05]" style={{ color: "#475569" }}>
                                                              <Bell className="w-5 h-5" />
                                                </button>
                                                <span
                                                                className="absolute -top-0.5 -right-0.5 w-[18px] h-[18px] rounded-full text-[10px] font-bold flex items-center justify-center"
                                                                style={{ background: "#f59e0b", color: "#000" }}
                                                              >3</span>
                                    </div>
                                    <button className="p-2 rounded-xl transition-all hover:bg-white/[0.05]" style={{ color: "#475569" }}>
                                                <MoreVertical className="w-5 h-5" />
                                    </button>
                          </div>
                </div>
        
          {/* SCROLLABLE CONTENT */}
              <div className="flex-1 overflow-y-auto">
                      <div className="px-8 py-6 space-y-6">
                      
                        {/* HERO ROW */}
                                <div className="flex items-start justify-between">
                                            <div>
                                                          <h1 className="text-[28px] font-bold text-white leading-tight">
                                                                          Bom dia, <span style={{ color: "#f59e0b" }}>Fernando!</span> ð
                                                          </h1>
                                                          <p className="text-[15px] mt-1" style={{ color: "#94a3b8" }}>
                                                                          Estou aqui para ajudar vocÃª a fazer<br />mais, em menos tempo.
                                                          </p>
                                            </div>
                                  {/* Orbital avatar decoration */}
                                            <div className="relative w-[140px] h-[140px] shrink-0 hidden xl:block">
                                                          <div
                                                                            className="absolute inset-0 rounded-full"
                                                                            style={{
                                                                                                background: "radial-gradient(circle at 35% 35%, rgba(59,130,246,0.6) 0%, rgba(139,92,246,0.4) 50%, transparent 70%)",
                                                                                                boxShadow: "0 0 60px rgba(59,130,246,0.4), 0 0 120px rgba(59,130,246,0.15)",
                                                                            }}
                                                                          />
                                                          <div
                                                                            className="absolute inset-4 rounded-full"
                                                                            style={{
                                                                                                background: "conic-gradient(from 0deg, transparent 60%, rgba(59,130,246,0.9) 75%, rgba(245,158,11,0.9) 85%, transparent 100%)",
                                                                                                animation: "spin-slow 3s linear infinite",
                                                                            }}
                                                                          />
                                                          <div
                                                                            className="absolute inset-[18px] rounded-full"
                                                                            style={{
                                                                                                background: "radial-gradient(circle at 35% 30%, rgba(147,197,253,0.8), rgba(59,130,246,0.5), rgba(139,92,246,0.3))",
                                                                                                boxShadow: "inset 0 0 30px rgba(59,130,246,0.5)",
                                                                            }}
                                                                          />
                                                          <div
                                                                            className="absolute inset-[35px] rounded-full"
                                                                            style={{
                                                                                                background: "radial-gradient(circle at 35% 35%, #bfdbfe, #3b82f6, #1e40af)",
                                                                                                boxShadow: "0 0 20px rgba(147,197,253,0.9), 0 0 40px rgba(59,130,246,0.6)",
                                                                            }}
                                                                          />
                                            </div>
                                </div>
                      
                        {/* STAT CARDS */}
                                <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                                  {statCards.map((s, i) => (
                        <div
                                          key={i}
                                          className="rounded-[18px] p-4 flex flex-col gap-2 cursor-pointer transition-all duration-200 hover:scale-[1.02]"
                                          style={{
                                                              background: s.bg || "rgba(255,255,255,0.04)",
                                                              border: "1px solid rgba(255,255,255,0.07)",
                                          }}
                                        >
                                        <s.icon className="w-5 h-5" style={{ color: s.color }} />
                                        <div className="text-[26px] font-bold text-white leading-none">{s.value}</div>
                                        <div className="text-[12px]" style={{ color: "#64748b" }}>{s.label}</div>
                        </div>
                      ))}
                                </div>
                      
                        {/* SEARCH BAR */}
                                <div
                                              className="rounded-[20px] p-4"
                                              style={{
                                                              background: "rgba(255,255,255,0.04)",
                                                              border: "1px solid rgba(255,255,255,0.08)",
                                              }}
                                            >
                                            <form onSubmit={handleSubmit}>
                                                          <input
                                                                            value={input}
                                                                            onChange={(e) => setInput(e.target.value)}
                                                                            placeholder="Como posso ajudar vocÃª hoje?"
                                                                            className="w-full bg-transparent text-white text-[15px] outline-none mb-3"
                                                                            style={{ "::placeholder": { color: "#475569" } } as React.CSSProperties}
                                                                          />
                                                          <div className="flex items-center justify-between">
                                                                          <div className="flex items-center gap-4">
                                                                                            <button type="button" className="text-slate-500 hover:text-slate-400 transition-colors">
                                                                                                                <Plus className="w-5 h-5" />
                                                                                              </button>
                                                                                            <button type="button" className="flex items-center gap-2 text-[13px] text-slate-500 hover:text-slate-400 transition-colors">
                                                                                                                <Grid3X3 className="w-4 h-4" />
                                                                                                                Ferramentas
                                                                                              </button>
                                                                          </div>
                                                                          <div className="flex items-center gap-2">
                                                                                            <button type="button" className="p-2 rounded-full text-slate-500 hover:text-slate-400 transition-colors">
                                                                                                                <Mic className="w-5 h-5" />
                                                                                              </button>
                                                                                            <button
                                                                                                                  type="submit"
                                                                                                                  className="w-11 h-11 rounded-full flex items-center justify-center transition-all hover:scale-105"
                                                                                                                  style={{
                                                                                                                                          background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
                                                                                                                                          boxShadow: "0 4px 15px rgba(59,130,246,0.4)",
                                                                                                                    }}
                                                                                                                >
                                                                                                                <Send className="w-4 h-4 text-white" />
                                                                                              </button>
                                                                          </div>
                                                          </div>
                                            </form>
                                </div>
                      
                        {/* ACTION CARDS */}
                                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
                                  {actionCards.map((a, i) => (
                        <button
                                          key={i}
                                          onClick={() => router.push(a.href)}
                                          className="rounded-[20px] p-5 text-left flex flex-col gap-3 cursor-pointer transition-all duration-200 hover:scale-[1.02] hover:border-white/20"
                                          style={{
                                                              background: a.bg,
                                                              border: "1px solid rgba(255,255,255,0.07)",
                                          }}
                                        >
                                        <a.icon className="w-7 h-7" style={{ color: a.color }} />
                                        <div>
                                                          <div className="text-[14px] font-semibold mb-0.5" style={{ color: a.titleColor || "#f1f5f9" }}>
                                                            {a.title}
                                                          </div>
                                                          <div className="text-[12px]" style={{ color: "#64748b" }}>{a.desc}</div>
                                        </div>
                        </button>
                      ))}
                                </div>
                      
                        {/* BOTTOM TWO COLUMNS */}
                                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                                
                                  {/* LEFT: Recent Activity */}
                                            <div
                                                            className="rounded-[20px] p-5"
                                                            style={{
                                                                              background: "rgba(255,255,255,0.03)",
                                                                              border: "1px solid rgba(255,255,255,0.07)",
                                                            }}
                                                          >
                                                          <div className="flex items-center justify-between mb-4">
                                                                          <div className="flex items-center gap-2">
                                                                                            <Activity className="w-4 h-4" style={{ color: "#60a5fa" }} />
                                                                                            <span className="text-[14px] font-semibold text-white">Atividade recente</span>
                                                                          </div>
                                                                          <button className="text-[12px] transition-colors hover:text-white" style={{ color: "#3b82f6" }}>
                                                                                            Ver tudo
                                                                          </button>
                                                          </div>
                                                          <div className="flex flex-col gap-1">
                                                            {recentActivity.map((item, i) => (
                                                                              <div key={i} className="flex items-center gap-3 py-2.5 rounded-xl px-2 hover:bg-white/[0.03] transition-all">
                                                                                                  <div
                                                                                                                          className="w-8 h-8 rounded-xl flex items-center justify-center shrink-0"
                                                                                                                          style={{ background: "rgba(255,255,255,0.05)" }}
                                                                                                                        >
                                                                                                                        <item.icon className="w-4 h-4" style={{ color: item.color }} />
                                                                                                    </div>
                                                                                                  <div className="flex-1 min-w-0">
                                                                                                                        <div className="text-[13px] font-medium text-white truncate">{item.title}</div>
                                                                                                                        <div className="text-[11px] truncate" style={{ color: "#64748b" }}>{item.sub}</div>
                                                                                                    </div>
                                                                                                  <div className="flex items-center gap-2 shrink-0">
                                                                                                                        <span className="text-[11px]" style={{ color: "#475569" }}>{item.time}</span>
                                                                                                    {item.status === "done" ? (
                                                                                                        <Check className="w-4 h-4 rounded-full" style={{ color: "#22c55e" }} />
                                                                                                      ) : (
                                                                                                        <Loader className="w-4 h-4 animate-spin" style={{ color: "#60a5fa" }} />
                                                                                                      )}
                                                                                                    </div>
                                                                              </div>
                                                                            ))}
                                                          </div>
                                            </div>
                                
                                  {/* RIGHT: Systems + Suggestions */}
                                            <div className="flex flex-col gap-4">
                                            
                                              {/* Connected Systems */}
                                                          <div
                                                                            className="rounded-[20px] p-5"
                                                                            style={{
                                                                                                background: "rgba(255,255,255,0.03)",
                                                                                                border: "1px solid rgba(255,255,255,0.07)",
                                                                            }}
                                                                          >
                                                                          <div className="flex items-center justify-between mb-4">
                                                                                            <div className="flex items-center gap-2">
                                                                                                                <Zap className="w-4 h-4" style={{ color: "#60a5fa" }} />
                                                                                                                <span className="text-[14px] font-semibold text-white">Sistemas conectados</span>
                                                                                              </div>
                                                                                            <button className="text-[12px] transition-colors hover:text-white" style={{ color: "#3b82f6" }}>
                                                                                                                Ver todos
                                                                                              </button>
                                                                          </div>
                                                                          <div className="grid grid-cols-2 gap-2">
                                                                            {connectedSystems.map((sys, i) => (
                                                                                                <div key={i} className="flex items-center gap-2.5 py-2 px-3 rounded-xl hover:bg-white/[0.03] transition-all">
                                                                                                                      <sys.icon className="w-4 h-4 shrink-0" style={{ color: "#64748b" }} />
                                                                                                                      <span className="text-[13px] text-white flex-1">{sys.name}</span>
                                                                                                                      <div className="flex items-center gap-1">
                                                                                                                                              <span
                                                                                                                                                                          className="w-2 h-2 rounded-full shrink-0"
                                                                                                                                                                          style={{
                                                                                                                                                                                                        background: "#22c55e",
                                                                                                                                                                                                        boxShadow: "0 0 6px rgba(34,197,94,0.7)",
                                                                                                                                                                            }}
                                                                                                                                                                        />
                                                                                                                                              <span className="text-[11px]" style={{ color: "#22c55e" }}>Online</span>
                                                                                                                        </div>
                                                                                                  </div>
                                                                                              ))}
                                                                          </div>
                                                          </div>
                                            
                                              {/* Suggestions */}
                                                          <div
                                                                            className="rounded-[20px] p-5"
                                                                            style={{
                                                                                                background: "rgba(255,255,255,0.03)",
                                                                                                border: "1px solid rgba(255,255,255,0.07)",
                                                                            }}
                                                                          >
                                                                          <div className="flex items-center justify-between mb-4">
                                                                                            <div className="flex items-center gap-2">
                                                                                                                <Star className="w-4 h-4" style={{ color: "#f59e0b" }} />
                                                                                                                <span className="text-[14px] font-semibold text-white">SugestÃµes para vocÃª</span>
                                                                                              </div>
                                                                                            <button className="text-[12px] transition-colors hover:text-white" style={{ color: "#3b82f6" }}>
                                                                                                                Ver todas
                                                                                              </button>
                                                                          </div>
                                                                          <div className="flex flex-col gap-2">
                                                                            {suggestions.map((sug, i) => (
                                                                                                <button
                                                                                                                        key={i}
                                                                                                                        className="flex items-center gap-3 py-2.5 px-3 rounded-xl hover:bg-white/[0.04] transition-all w-full text-left"
                                                                                                                      >
                                                                                                                      <sug.icon className="w-5 h-5 shrink-0" style={{ color: sug.color }} />
                                                                                                                      <div className="flex-1 min-w-0">
                                                                                                                                              <div className="text-[13px] font-medium text-white">{sug.title}</div>
                                                                                                                                              <div className="text-[11px]" style={{ color: "#64748b" }}>{sug.sub}</div>
                                                                                                                        </div>
                                                                                                                      <ArrowRight className="w-4 h-4 shrink-0" style={{ color: "#475569" }} />
                                                                                                  </button>
                                                                                              ))}
                                                                          </div>
                                                          </div>
                                            </div>
                                </div>
                      
                      </div>
              </div>
        
          {/* VOICE BAR */}
              <div
                        className="shrink-0 mx-6 mb-4 mt-2 rounded-[50px] px-5 py-3"
                        style={{
                                    background: "rgba(255,255,255,0.04)",
                                    border: "1px solid rgba(59,130,246,0.2)",
                                    backdropFilter: "blur(20px)",
                        }}
                      >
                      <div className="flex items-center gap-4">
                                <button className="flex items-center gap-2 text-[13px] py-1 px-3 rounded-full transition-all hover:bg-white/[0.05]" style={{ color: "#64748b" }}>
                                            <Keyboard className="w-4 h-4" />
                                            Teclado
                                </button>
                                <div className="flex-1 flex justify-center relative">
                                  {/* Sound wave dots */}
                                            <div className="flex items-center gap-1 absolute left-1/2 -translate-x-1/2">
                                              {[...Array(20)].map((_, i) => (
                                        <div
                                                            key={i}
                                                            className="w-0.5 rounded-full"
                                                            style={{
                                                                                  height: `${Math.random() * 16 + 4}px`,
                                                                                  background: i < 8 || i > 12 ? "rgba(59,130,246,0.3)" : "#3b82f6",
                                                                                  opacity: 0.7,
                                                            }}
                                                          />
                                      ))}
                                            </div>
                                            <button
                                                            className="relative z-10 w-12 h-12 rounded-full flex items-center justify-center transition-all hover:scale-105"
                                                            style={{
                                                                              background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
                                                                              boxShadow: "0 0 30px rgba(59,130,246,0.5), 0 0 60px rgba(59,130,246,0.2)",
                                                            }}
                                                          >
                                                          <Mic className="w-5 h-5 text-white" />
                                            </button>
                                </div>
                                <button className="flex items-center gap-2 text-[13px] py-1 px-3 rounded-full transition-all hover:bg-white/[0.05]" style={{ color: "#64748b" }}>
                                            <Globe className="w-4 h-4" />
                                            Idioma
                                </button>
                      </div>
                      <p className="text-center text-[12px] mt-2" style={{ color: "#475569" }}>Clique ou fale para conversar</p>
              </div>
        
          {/* Footer */}
              <div className="text-center pb-3 text-[11px]" style={{ color: "#334155" }}>
                      KairÃ³s Assistente Inteligente â¢ v1.0.0 â¡
              </div>
        </div>
      )
}
