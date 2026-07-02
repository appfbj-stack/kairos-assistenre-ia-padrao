"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { useUIStore } from "@/stores/uiStore"
import {
    Home,
    MessageSquare,
    Bot,
    Wrench,
    FileText,
    Settings,
    Cpu,
    Zap,
    History,
    BarChart2,
    ChevronDown,
    Sun,
    LogOut,
    Circle,
} from "lucide-react"
import { ScrollArea } from "@/components/ui/scroll-area"

const navItems = [
  { href: "/", label: "InÃ­cio", icon: Home },
  { href: "/chat", label: "Conversas", icon: MessageSquare },
  { href: "/agentes", label: "Agentes", icon: Bot },
  { href: "/ferramentas", label: "Ferramentas", icon: Wrench },
  { href: "/documentos", label: "Documentos", icon: FileText },
  { href: "/aion", label: "MCPs", icon: Cpu },
  { href: "/skills", label: "Skills", icon: Zap },
  { href: "/historico", label: "HistÃ³rico", icon: History },
  { href: "/painel", label: "Painel", icon: BarChart2 },
  { href: "/configuracoes", label: "ConfiguraÃ§Ãµes", icon: Settings },
  ]

export function Sidebar() {
    const pathname = usePathname()
    const sidebarOpen = useUIStore((s) => s.sidebarOpen)
    const setSidebarOpen = useUIStore((s) => s.setSidebarOpen)

  return (
        <>
          {sidebarOpen && (
                  <div
                              className="fixed inset-0 z-40 bg-black/60 lg:hidden"
                              onClick={() => setSidebarOpen(false)}
                            />
                )}
              <aside
                        className={cn(
                                    "fixed top-0 left-0 z-50 h-full w-[185px] flex flex-col",
                                    "transition-transform duration-300 ease-in-out",
                                    "lg:translate-x-0 lg:static lg:z-auto",
                                    "border-r border-white/[0.06]",
                                    sidebarOpen ? "translate-x-0" : "-translate-x-full",
                                  )}
                        style={{ background: "#06061a" }}
                      >
                {/* Logo */}
                      <div className="flex flex-col items-center px-5 pt-7 pb-6">
                                <div
                                              className="w-[72px] h-[72px] rounded-full flex items-center justify-center mb-3 relative"
                                              style={{
                                                              background: "radial-gradient(circle at 35% 35%, #1e3a8a, #06061a)",
                                                              boxShadow: "0 0 40px rgba(59,130,246,0.5), 0 0 80px rgba(59,130,246,0.15), inset 0 0 30px rgba(139,92,246,0.2)",
                                              }}
                                            >
                                  {/* Orbit ring */}
                                            <div
                                                            className="absolute inset-0 rounded-full"
                                                            style={{
                                                                              background: "conic-gradient(from 0deg, transparent 60%, rgba(59,130,246,0.8) 80%, rgba(245,158,11,0.8) 90%, transparent 100%)",
                                                                              animation: "spin-slow 3s linear infinite",
                                                            }}
                                                          />
                                            <div
                                                            className="absolute inset-[3px] rounded-full"
                                                            style={{ background: "radial-gradient(circle at 35% 35%, #1e3a8a, #06061a)" }}
                                                          />
                                  {/* Inner glow orb */}
                                            <div
                                                            className="relative z-10 w-10 h-10 rounded-full flex items-center justify-center"
                                                            style={{
                                                                              background: "radial-gradient(circle at 40% 30%, rgba(99,179,237,0.9), rgba(59,130,246,0.6), rgba(139,92,246,0.4))",
                                                                              boxShadow: "0 0 20px rgba(59,130,246,0.8)",
                                                            }}
                                                          >
                                                          <div
                                                                            className="w-5 h-5 rounded-full"
                                                                            style={{
                                                                                                background: "radial-gradient(circle at 35% 35%, #93c5fd, #3b82f6, #1d4ed8)",
                                                                                                boxShadow: "0 0 15px rgba(147,197,253,0.9)",
                                                                            }}
                                                                          />
                                            </div>
                                </div>
                                <h2 className="text-[17px] font-bold text-white tracking-wide">KairÃ³s</h2>
                                <p className="text-[11px] text-center mt-0.5" style={{ color: "#64748b" }}>
                                            InteligÃªncia que age
                                            <br />no momento certo.
                                </p>
                      </div>
              
                {/* Nav */}
                      <ScrollArea className="flex-1 px-3">
                                <nav className="flex flex-col gap-0.5">
                                  {navItems.map((item) => {
                                      const isActive = pathname === item.href
                                                      return (
                                                                        <Link
                                                                                            key={item.href}
                                                                                            href={item.href}
                                                                                            onClick={() => setSidebarOpen(false)}
                                                                                          >
                                                                                          <div
                                                                                                                className={cn(
                                                                                                                                        "flex items-center gap-3 px-3 py-2.5 rounded-xl text-[13.5px] font-medium transition-all duration-200 cursor-pointer w-full",
                                                                                                                                        isActive
                                                                                                                                          ? "text-white"
                                                                                                                                          : "text-slate-500 hover:text-slate-300 hover:bg-white/[0.04]"
                                                                                                                                      )}
                                                                                                                style={isActive ? {
                                                                                                                                        background: "linear-gradient(135deg, rgba(59,130,246,0.22) 0%, rgba(139,92,246,0.12) 100%)",
                                                                                                                                        borderLeft: "3px solid #3b82f6",
                                                                                                                                        paddingLeft: "9px",
                                                                                                                  } : {}}
                                                                                                              >
                                                                                                              <item.icon
                                                                                                                                      className="w-[17px] h-[17px] shrink-0"
                                                                                                                                      style={{ color: isActive ? "#60a5fa" : undefined }}
                                                                                                                                    />
                                                                                            {item.label}
                                                                                            </div>
                                                                        </Link>
                                                                      )
                                  })}
                                </nav>
                      </ScrollArea>
              
                {/* User profile */}
                      <div className="px-3 py-3 border-t border-white/[0.05]">
                                <div
                                              className="flex items-center gap-2.5 px-3 py-2.5 rounded-xl cursor-pointer transition-all hover:bg-white/[0.04]"
                                            >
                                            <div
                                                            className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold shrink-0"
                                                            style={{
                                                                              background: "linear-gradient(135deg, #1e40af, #3b82f6)",
                                                                              boxShadow: "0 0 12px rgba(59,130,246,0.4)",
                                                            }}
                                                          >
                                                          F
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                          <p className="text-[13px] font-semibold text-white truncate">Fernando</p>
                                                          <p className="text-[11px] truncate" style={{ color: "#64748b" }}>Administrador</p>
                                            </div>
                                            <ChevronDown className="w-3.5 h-3.5 shrink-0" style={{ color: "#475569" }} />
                                </div>
                      </div>
              
                {/* Status bar */}
                      <div className="px-4 py-3 border-t border-white/[0.05]">
                                <div className="flex items-center gap-2 mb-1">
                                            <span
                                                            className="w-2 h-2 rounded-full shrink-0"
                                                            style={{
                                                                              background: "#22c55e",
                                                                              boxShadow: "0 0 8px rgba(34,197,94,0.7)",
                                                            }}
                                                          />
                                            <span className="text-[12px] font-semibold" style={{ color: "#22c55e" }}>KairÃ³s Online</span>
                                </div>
                                <p className="text-[11px] pl-4" style={{ color: "#475569" }}>Todos os sistemas operando</p>
                      </div>
              
                {/* Bottom actions */}
                      <div className="flex items-center justify-between px-5 py-3 border-t border-white/[0.05]">
                                <button className="p-1.5 rounded-lg transition-all hover:bg-white/[0.05]" style={{ color: "#475569" }}>
                                            <Sun className="w-4 h-4" />
                                </button>
                                <button className="p-1.5 rounded-lg transition-all hover:bg-white/[0.05]" style={{ color: "#475569" }}>
                                            <LogOut className="w-4 h-4" />
                                </button>
                      </div>
              </aside>
        </>
      )
}
