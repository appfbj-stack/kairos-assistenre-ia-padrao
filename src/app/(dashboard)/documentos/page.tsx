import { FileText } from "lucide-react"

export default function DocumentosPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-full px-4 py-16">
      <div className="w-16 h-16 rounded-2xl glass flex items-center justify-center mb-4">
        <FileText className="w-7 h-7 text-primary-light" />
      </div>
      <h1 className="text-xl font-semibold mb-2">Documentos</h1>
      <p className="text-sm text-muted-foreground text-center max-w-md">
        Gerencie seus documentos e arquivos para o assistente consultar.
      </p>
    </div>
  )
}
