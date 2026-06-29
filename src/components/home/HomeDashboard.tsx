"use client"

import { AvatarCanvas } from "@/components/avatar/AvatarCanvas"
import { useUIStore } from "@/stores/uiStore"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { MessageSquare, Sparkles, ArrowRight } from "lucide-react"
import { useState } from "react"

const quickActions = [
  { label: "Iniciar conversa", icon: MessageSquare, href: "/chat" },
  { label: "Explorar ferramentas", icon: Sparkles, href: "/ferramentas" },
]

export function HomeDashboard() {
  const router = useRouter()
  const setActivePanel = useUIStore((s) => s.setActivePanel)
  const [input, setInput] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return
    setActivePanel("chat")
    router.push(`/chat?q=${encodeURIComponent(input.trim())}`)
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-full px-4 py-8">
      <div className="mb-6">
        <AvatarCanvas />
      </div>
      <h1 className="text-2xl font-bold mb-1 text-center">
        Olá, eu sou o <span className="text-gradient-hero">Kairos</span>
      </h1>
      <p className="text-sm text-muted-foreground mb-8 text-center max-w-md">
        Seu assistente inteligente. Como posso ajudar hoje?
      </p>

      <form onSubmit={handleSubmit} className="w-full max-w-lg mb-8">
        <div className="relative">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Digite sua pergunta..."
            className="glass border-glass-border pr-12 h-12 text-sm placeholder:text-muted-foreground"
          />
          <Button
            type="submit"
            size="icon"
            className="absolute right-1.5 top-1/2 -translate-y-1/2 h-9 w-9 gradient-hero hover:opacity-90 text-white"
          >
            <ArrowRight className="w-4 h-4" />
          </Button>
        </div>
      </form>

      <div className="flex gap-3">
        {quickActions.map((action) => (
          <Button
            key={action.label}
            variant="ghost"
            onClick={() => router.push(action.href)}
            className="glass glass-hover gap-2 px-4 py-3 h-auto text-sm font-normal text-foreground/80"
          >
            <action.icon className="w-4 h-4 text-primary-light" />
            {action.label}
          </Button>
        ))}
      </div>
    </div>
  )
}
