"use client"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Send,
  Loader2,
  Mic,
  Square,
  ImagePlus,
  Paperclip,
  FileText,
  X,
} from "lucide-react"
import { useChatStore, type Attachment } from "@/stores/chatStore"
import { useUIStore } from "@/stores/uiStore"
import {
  sendMessageStream,
  sendMultimodalVoice,
  sendMultimodalVision,
  sendMultimodalDocument,
} from "@/lib/api"

export function ChatInput() {
  const [input, setInput] = useState("")
  const [recording, setRecording] = useState(false)
  const [attachments, setAttachments] = useState<Attachment[]>([])
  const [uploading, setUploading] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const fileRef = useRef<HTMLInputElement>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])

  const addMessage = useChatStore((s) => s.addMessage)
  const appendToLastMessage = useChatStore((s) => s.appendToLastMessage)
  const setStreaming = useChatStore((s) => s.setStreaming)
  const isStreaming = useChatStore((s) => s.isStreaming)
  const setAvatarState = useUIStore((s) => s.setAvatarState)

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream, { mimeType: "audio/webm" })
      chunksRef.current = []
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }
      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" })
        const name = `audio-${Date.now()}.webm`
        const reader = new FileReader()
        reader.onloadend = () => {
          setAttachments((prev) => [
            ...prev,
            { type: "audio", name, data: reader.result as string, mime: "audio/webm" },
          ])
        }
        reader.readAsDataURL(blob)
        stream.getTracks().forEach((t) => t.stop())
      }
      recorder.start()
      mediaRecorderRef.current = recorder
      setRecording(true)
    } catch {
      console.error("Microphone access denied")
    }
  }

  const stopRecording = () => {
    mediaRecorderRef.current?.stop()
    setRecording(false)
  }

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const type = file.type.startsWith("image/")
      ? "image"
      : /pdf|docx?|xlsx?|csv|txt/i.test(file.name)
        ? "document"
        : "image"
    const reader = new FileReader()
    reader.onloadend = () => {
      setAttachments((prev) => [
        ...prev,
        { type, name: file.name, data: reader.result as string, mime: file.type },
      ])
    }
    reader.readAsDataURL(file)
    if (fileRef.current) fileRef.current.value = ""
  }

  const removeAttachment = (index: number) => {
    setAttachments((prev) => prev.filter((_, i) => i !== index))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const text = input.trim()
    if ((!text && attachments.length === 0) || isStreaming || uploading) return

    const hasAudio = attachments.some((a) => a.type === "audio")
    const hasImage = attachments.some((a) => a.type === "image")
    const hasDoc = attachments.some((a) => a.type === "document")

    const userMsg = text || (hasAudio ? "🎤 Mensagem de voz" : "📎 Arquivo anexado")

    setInput("")
    addMessage({ role: "user", content: userMsg, attachments: [...attachments] })
    addMessage({ role: "assistant", content: "" })
    setStreaming(true)
    setAvatarState("thinking")

    try {
      if (hasAudio) {
        const audioAtt = attachments.find((a) => a.type === "audio")!
        const blob = await (await fetch(audioAtt.data!)).blob()
        await sendMultimodalVoice(blob, (chunk) => appendToLastMessage(chunk))
        setAvatarState("speaking")
      } else if (hasImage && !text) {
        const imgAtt = attachments.find((a) => a.type === "image")!
        const file = await (await fetch(imgAtt.data!)).blob()
        const f = new File([file], imgAtt.name, { type: imgAtt.mime })
        await sendMultimodalVision(f, (chunk) => appendToLastMessage(chunk))
      } else if (hasDoc && !text) {
        const docAtt = attachments.find((a) => a.type === "document")!
        const file = await (await fetch(docAtt.data!)).blob()
        const f = new File([file], docAtt.name, { type: docAtt.mime })
        await sendMultimodalDocument(f, (chunk) => appendToLastMessage(chunk))
      } else {
        await sendMessageStream(text, (chunk) => appendToLastMessage(chunk))
      }
    } catch {
      appendToLastMessage("\n\n[Erro ao conectar com o servidor]")
    } finally {
      setStreaming(false)
      setAttachments([])
      setAvatarState("idle")
      inputRef.current?.focus()
    }
  }

  const attachmentIcon = (type: string) => {
    if (type === "image") return <ImagePlus className="w-3 h-3" />
    if (type === "audio") return <Mic className="w-3 h-3" />
    return <FileText className="w-3 h-3" />
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-2">
      {attachments.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {attachments.map((att, i) => (
            <div
              key={i}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-accent/50 text-xs text-muted-foreground"
            >
              {attachmentIcon(att.type)}
              <span className="max-w-[120px] truncate">{att.name}</span>
              <button
                type="button"
                onClick={() => removeAttachment(i)}
                className="ml-0.5 hover:text-foreground"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          ))}
        </div>
      )}
      <div className="flex gap-2 items-end">
        <div className="flex gap-1">
          <Button
            type="button"
            size="icon"
            variant="ghost"
            className="h-11 w-10 shrink-0 text-muted-foreground hover:text-foreground"
            onClick={() => fileRef.current?.click()}
            disabled={isStreaming || uploading}
            title="Anexar imagem ou documento"
          >
            <Paperclip className="w-4 h-4" />
          </Button>
          <input
            ref={fileRef}
            type="file"
            accept="image/*,.pdf,.doc,.docx,.xls,.xlsx,.csv,.txt"
            className="hidden"
            onChange={handleFileSelect}
          />
          <Button
            type="button"
            size="icon"
            variant={recording ? "destructive" : "ghost"}
            className={`h-11 w-10 shrink-0 ${
              recording ? "animate-pulse" : "text-muted-foreground hover:text-foreground"
            }`}
            onClick={recording ? stopRecording : startRecording}
            disabled={isStreaming || uploading}
            title={recording ? "Parar gravação" : "Gravar áudio"}
          >
            {recording ? <Square className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
          </Button>
        </div>
        <Input
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={recording ? "Gravando áudio..." : "Digite sua mensagem..."}
          disabled={isStreaming || recording || uploading}
          className="glass border-glass-border h-11 text-sm placeholder:text-muted-foreground"
        />
        <Button
          type="submit"
          size="icon"
          disabled={isStreaming || uploading || recording || (!input.trim() && attachments.length === 0)}
          className="h-11 w-11 shrink-0 gradient-hero hover:opacity-90 text-white"
        >
          {isStreaming || uploading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Send className="w-4 h-4" />
          )}
        </Button>
      </div>
    </form>
  )
}
