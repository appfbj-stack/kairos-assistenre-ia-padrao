"use client"

import { useUIStore } from "@/stores/uiStore"
import { Menu } from "lucide-react"

export function Header() {
    const toggleSidebar = useUIStore((s) => s.toggleSidebar)

  return (
        <header
                className="flex items-center px-4 py-3 lg:hidden"
                style={{
                          background: "#07071a",
                          borderBottom: "1px solid rgba(255,255,255,0.06)",
                }}
              >
              <button
                        onClick={toggleSidebar}
                        className="p-2 rounded-xl transition-all hover:bg-white/[0.05]"
                        style={{ color: "#64748b" }}
                      >
                      <Menu className="w-5 h-5" />
              </button>button>
              <div className="flex items-center gap-2 ml-3">
                      <div
                                  className="w-7 h-7 rounded-full flex items-center justify-center"
                                  style={{
                                                background: "radial-gradient(circle at 35% 35%, #1e3a8a, #06061a)",
                                                boxShadow: "0 0 12px rgba(59,130,246,0.5)",
                                  }}
                                />
                      <span className="text-[15px] font-semibold text-white">Kairós</span>span>
              </div>div>
        </header>header>
      )
}</header>
