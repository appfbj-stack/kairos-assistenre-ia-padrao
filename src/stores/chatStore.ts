import { create } from "zustand"

export interface Attachment {
  type: "image" | "audio" | "document"
  name: string
  url?: string
  data?: string // base64
  mime?: string
}

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  attachments?: Attachment[]
  timestamp: number
}

interface ChatState {
  messages: Message[]
  isStreaming: boolean
  addMessage: (msg: Omit<Message, "id" | "timestamp">) => void
  appendToLastMessage: (content: string) => void
  setStreaming: (v: boolean) => void
  clearMessages: () => void
}

let msgCounter = 0

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isStreaming: false,
  addMessage: (msg) =>
    set((s) => ({
      messages: [
        ...s.messages,
        { ...msg, id: `msg-${++msgCounter}`, timestamp: Date.now() },
      ],
    })),
  appendToLastMessage: (content) =>
    set((s) => {
      const msgs = [...s.messages]
      const last = msgs[msgs.length - 1]
      if (last) last.content += content
      return { messages: msgs }
    }),
  setStreaming: (v) => set({ isStreaming: v }),
  clearMessages: () => set({ messages: [] }),
}))
