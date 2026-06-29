const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || ""

function headers() {
  return {
    Authorization: `Bearer ${API_KEY}`,
  }
}

export async function sendMessageStream(
  message: string,
  onChunk: (text: string) => void,
  conversationId?: string,
  signal?: AbortSignal,
) {
  const res = await fetch(`${API_BASE}/api/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...headers(),
    },
    body: JSON.stringify({ message, conversation_id: conversationId }),
    signal,
  })
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  const reader = res.body?.getReader()
  const decoder = new TextDecoder()
  if (!reader) throw new Error("No response body")
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    const text = decoder.decode(value, { stream: true })
    onChunk(text)
  }
}

export async function sendMultimodalVoice(
  audioBlob: Blob,
  onChunk: (text: string) => void,
  signal?: AbortSignal,
) {
  const form = new FormData()
  form.append("file", audioBlob, "recording.webm")
  const res = await fetch(`${API_BASE}/api/multimodal/voice`, {
    method: "POST",
    headers: headers(),
    body: form,
    signal,
  })
  if (!res.ok) throw new Error(`Voice API error: ${res.status}`)
  const data = await res.json()
  if (data.text) onChunk(data.text)
  return data
}

export async function sendMultimodalVision(
  file: File,
  onChunk: (text: string) => void,
  signal?: AbortSignal,
) {
  const form = new FormData()
  form.append("file", file)
  const res = await fetch(`${API_BASE}/api/multimodal/vision`, {
    method: "POST",
    headers: headers(),
    body: form,
    signal,
  })
  if (!res.ok) throw new Error(`Vision API error: ${res.status}`)
  const data = await res.json()
  if (data.description) onChunk(data.description)
  return data
}

export async function sendMultimodalDocument(
  file: File,
  onChunk: (text: string) => void,
  signal?: AbortSignal,
) {
  const form = new FormData()
  form.append("file", file)
  const res = await fetch(`${API_BASE}/api/multimodal/document`, {
    method: "POST",
    headers: headers(),
    body: form,
    signal,
  })
  if (!res.ok) throw new Error(`Document API error: ${res.status}`)
  const data = await res.json()
  if (data.summary) onChunk(data.summary)
  return data
}

export async function healthCheck() {
  const res = await fetch(`${API_BASE}/health`)
  return res.ok
}
