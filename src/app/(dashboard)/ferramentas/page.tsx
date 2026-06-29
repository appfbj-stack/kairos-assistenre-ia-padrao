import { Wrench } from "lucide-react"

export default function FerramentasPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-full px-4 py-16">
      <div className="w-16 h-16 rounded-2xl glass flex items-center justify-center mb-4">
        <Wrench className="w-7 h-7 text-primary-light" />
      </div>
      <h1 className="text-xl font-semibold mb-2">Ferramentas</h1>
      <p className="text-sm text-muted-foreground text-center max-w-md">
        Em breve você poderá gerenciar ferramentas e integrações do assistente.
      </p>
    </div>
  )
}
