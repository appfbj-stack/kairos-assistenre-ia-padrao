import { Suspense } from "react"
import { ChatInterface } from "@/components/chat/ChatInterface"

export default function ChatPage() {
  return (
    <div className="flex flex-col h-full">
      <Suspense fallback={<div className="flex-1 flex items-center justify-center text-muted-foreground text-sm">Carregando...</div>}>
        <ChatInterface />
      </Suspense>
    </div>
  )
}
