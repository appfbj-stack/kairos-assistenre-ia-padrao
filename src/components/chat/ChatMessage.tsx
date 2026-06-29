"use client"

import { cn } from "@/lib/utils"
import { User, Bot, ImageIcon, FileText, Mic } from "lucide-react"
import type { Message } from "@/stores/chatStore"

interface ChatMessageProps {
  message: Message
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user"

  return (
    <div className={cn("flex gap-3", isUser ? "justify-end" : "justify-start")}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full gradient-hero flex items-center justify-center shrink-0 mt-0.5">
          <Bot className="w-4 h-4 text-white" />
        </div>
      )}
      <div
        className={cn(
          "max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed",
          isUser
            ? "bg-primary text-primary-foreground rounded-br-md"
            : "bg-card text-card-foreground border border-glass-border rounded-bl-md",
        )}
      >
        {message.attachments && message.attachments.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-2">
            {message.attachments.map((att, i) => {
              if (att.type === "image" && att.data) {
                return (
                  <div key={i} className="relative group">
                    <img
                      src={att.data}
                      alt={att.name}
                      className="max-w-[200px] max-h-[200px] rounded-lg object-cover border border-glass-border"
                    />
                    <span className="absolute bottom-1 left-1 px-1.5 py-0.5 bg-black/60 text-[10px] text-white rounded">
                      {att.name}
                    </span>
                  </div>
                )
              }
              return (
                <div
                  key={i}
                  className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-accent/50 text-xs"
                >
                  {att.type === "audio" ? (
                    <Mic className="w-3.5 h-3.5" />
                  ) : att.type === "image" ? (
                    <ImageIcon className="w-3.5 h-3.5" />
                  ) : (
                    <FileText className="w-3.5 h-3.5" />
                  )}
                  {att.name}
                </div>
              )
            })}
          </div>
        )}
        <div className="whitespace-pre-wrap">{message.content || "..."}</div>
      </div>
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center shrink-0 mt-0.5">
          <User className="w-4 h-4 text-muted-foreground" />
        </div>
      )}
    </div>
  )
}
