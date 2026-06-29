"use client"

import { useEffect, useRef } from "react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { ChatMessage } from "./ChatMessage"
import { ChatInput } from "./ChatInput"
import { useChatStore } from "@/stores/chatStore"
import { useUIStore } from "@/stores/uiStore"
import { useSearchParams } from "next/navigation"
import { AvatarCanvas } from "@/components/avatar/AvatarCanvas"
import { Bot, Mic, Image, Sparkles } from "lucide-react"
import { cn } from "@/lib/utils"

export function ChatInterface() {
  const messages = useChatStore((s) => s.messages)
  const addMessage = useChatStore((s) => s.addMessage)
  const isStreaming = useChatStore((s) => s.isStreaming)
  const avatarState = useUIStore((s) => s.avatarState)
  const scrollRef = useRef<HTMLDivElement>(null)
  const searchParams = useSearchParams()

  useEffect(() => {
    const q = searchParams.get("q")
    if (q && messages.length === 0) {
      addMessage({ role: "user", content: q })
    }
  }, [])

  useEffect(() => {
    if (scrollRef.current) {
      const el = scrollRef.current.querySelector("[data-radix-scroll-area-viewport]")
      if (el) el.scrollTop = el.scrollHeight
    }
  }, [messages])

  if (messages.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center flex-1 px-4 py-8">
        <div className="mb-6">
          <AvatarCanvas />
        </div>
        <h2 className="text-xl font-semibold mb-1">
          <span className="text-gradient-hero">Kairos</span>
        </h2>
        <p className="text-sm text-muted-foreground text-center max-w-sm mb-6">
          Estou pronto para ajudar. Pergunte, envie uma imagem, documento ou use sua voz.
        </p>
        <div className="flex gap-3 text-xs text-muted-foreground">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-accent/50">
            <Mic className="w-3 h-3" />
            Voz
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-accent/50">
            <Image className="w-3 h-3" />
            Imagem
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-accent/50">
            <Sparkles className="w-3 h-3" />
            Documentos
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col flex-1 h-full">
      {isStreaming && (
        <div className="flex justify-center py-2">
          <div className="w-12 h-12">
            <AvatarCanvas />
          </div>
        </div>
      )}
      <ScrollArea className="flex-1 px-4 py-4" ref={scrollRef}>
        <div className="flex flex-col gap-4 max-w-3xl mx-auto">
          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} />
          ))}
          {avatarState === "speaking" && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground animate-pulse">
              <Bot className="w-3 h-3" />
              Reproduzindo resposta em áudio...
            </div>
          )}
        </div>
      </ScrollArea>
      <div className="px-4 py-3 border-t border-glass-border">
        <div className="max-w-3xl mx-auto">
          <ChatInput />
        </div>
      </div>
    </div>
  )
}
