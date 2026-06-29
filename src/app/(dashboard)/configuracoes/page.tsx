import { Settings } from "lucide-react"

export default function ConfiguracoesPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-full px-4 py-16">
      <div className="w-16 h-16 rounded-2xl glass flex items-center justify-center mb-4">
        <Settings className="w-7 h-7 text-primary-light" />
      </div>
      <h1 className="text-xl font-semibold mb-2">Configurações</h1>
      <p className="text-sm text-muted-foreground text-center max-w-md">
        Personalize seu assistente e suas preferências.
      </p>
    </div>
  )
}
