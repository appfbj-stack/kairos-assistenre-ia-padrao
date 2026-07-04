"use client"

import { KairosChat } from "@kairos/chat-ui"
import "@kairos/chat-ui/styles.css"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || "kairos-b4cad9a30caf4491809f90ff"

export function ClientChatPage() {
  return (
    <div className="flex flex-col h-full">
      <KairosChat
        config={{
          app: { name: "Kairós Assistente", slug: "assistente" },
          tenant: { name: "Kairós", slug: "kairos" },
          user: {
            id: "1",
            name: "Usuário",
            email: "usuario@kairos.app",
          },
          model: { name: "Kairós IA", provider: "OpenRouter" },
          permissions: {
            canUseVoice: true,
            canUploadImages: true,
            canUploadDocuments: true,
            canUseTools: true,
            canAccessHistory: true,
          },
          api: {
            baseUrl: API_URL,
            apiKey: API_KEY,
          },
          suggestions: [
            {
              id: "1",
              label: "Agendar reunião",
              prompt: "Me ajude a agendar uma reunião para amanhã às 10h",
              icon: "calendar",
            },
            {
              id: "2",
              label: "Resumir documento",
              prompt: "Resuma este documento para mim",
              icon: "document",
            },
            {
              id: "3",
              label: "Gerar relatório",
              prompt: "Gere um relatório sobre o último mês",
              icon: "chart",
            },
            {
              id: "4",
              label: "Criar evento",
              prompt: "Crie um evento para o próximo sábado",
              icon: "calendar",
            },
          ],
        }}
      />
    </div>
  )
}
