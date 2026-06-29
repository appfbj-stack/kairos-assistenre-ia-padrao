"use client"

import { useUIStore } from "@/stores/uiStore"
import { Button } from "@/components/ui/button"
import { Menu, Bot } from "lucide-react"

export function Header() {
  const toggleSidebar = useUIStore((s) => s.toggleSidebar)

  return (
    <header className="flex items-center justify-between px-4 py-3 border-b border-glass-border lg:hidden bg-background/80 backdrop-blur-xl">
      <div className="flex items-center gap-3">
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleSidebar}
          className="text-foreground/70 hover:text-foreground"
        >
          <Menu className="w-5 h-5" />
        </Button>
        <div className="flex items-center gap-2">
          <div className="flex items-center justify-center w-7 h-7 rounded-lg gradient-hero">
            <Bot className="w-4 h-4 text-white" />
          </div>
          <span className="text-sm font-semibold">Kairos</span>
        </div>
      </div>
    </header>
  )
}
