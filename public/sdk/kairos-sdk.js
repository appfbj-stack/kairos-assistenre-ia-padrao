(function (global) {
  "use strict"

  class KairosClient {
    constructor(config) {
      this.apiUrl = config.apiUrl || "https://api.assistente.fbautomacao.space"
      this.apiKey = config.apiKey || ""
      this.appSlug = config.appSlug || ""
      this.appName = config.appName || ""
      this.ambiente = config.ambiente || "production"
      this.online = navigator.onLine
      const self = this
      window.addEventListener("online", () => { self.online = true })
      window.addEventListener("offline", () => { self.online = false })
    }

    async request(method, path, body) {
      const res = await fetch(`${this.apiUrl}${path}`, {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${this.apiKey}`,
        },
        body: body ? JSON.stringify(body) : undefined,
      })
      if (!res.ok) {
        const text = await res.text().catch(() => "")
        throw new Error(`Kairos erro ${res.status}: ${text.slice(0, 200)}`)
      }
      return res.json()
    }

    async requestStream(path, body, onChunk) {
      const res = await fetch(`${this.apiUrl}${path}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${this.apiKey}`,
        },
        body: JSON.stringify(body),
      })
      if (!res.ok) throw new Error(`Kairos erro ${res.status}`)
      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        onChunk(decoder.decode(value, { stream: true }))
      }
    }

    async registerContext(appName, modules, context) {
      return this.request("POST", "/api/apps/context", {
        app_slug: this.appSlug,
        app_name: appName || this.appName,
        modules,
        context,
      })
    }

    async registerSession(userId, userName, userEmail, userRole, modules, departments) {
      return this.request("POST", "/api/apps/session", {
        app_slug: this.appSlug,
        user_id: userId,
        user_name: userName,
        user_email: userEmail,
        user_role: userRole || "member",
        modules: modules || [],
        departments: departments || [],
      })
    }

    async registerApp(name, slug, originUrl, context) {
      return this.request("POST", "/api/tools/apps/register", { name, slug, origin_url: originUrl, context })
    }

    async registerTool(appSlug, name, description, schema, endpoint, method, headers) {
      return this.request("POST", "/api/tools/register", {
        app_slug: appSlug,
        name,
        description,
        schema,
        endpoint,
        method: method || "POST",
        headers: headers || {},
      })
    }

    async listTools() {
      return this.request("GET", "/api/tools/list")
    }

    async sendMessage(message, conversationId) {
      return this.request("POST", "/api/chat", {
        message,
        conversation_id: conversationId,
        app_slug: this.appSlug,
      })
    }

    async sendMessageStream(message, conversationId, onChunk) {
      return this.requestStream("/api/chat/stream", {
        message,
        conversation_id: conversationId,
        app_slug: this.appSlug,
      }, onChunk)
    }

    async getAuditLogs(params) {
      const q = new URLSearchParams(params || {}).toString()
      return this.request("GET", `/api/audit/logs?${q}`)
    }
  }

  function renderWidget(client, containerId, options) {
    const container = document.getElementById(containerId)
    if (!container) {
      console.warn("Kairos: container not found:", containerId)
      return
    }

    const shadow = container.attachShadow({ mode: "open" })
    const suggestions = options.suggestions || [
      "Quantos membros temos?",
      "O que esta programado para hoje?",
      "Resumo financeiro do mes",
    ]

    shadow.innerHTML = `
<style>
:host { --primary: #1e40af; --primary-light: #3b82f6; --bg: #0a0a1a; }
* { box-sizing: border-box; margin: 0; padding: 0; }
.kairos-widget { position: fixed; bottom: 20px; right: 20px; z-index: 999999; font-family: system-ui, -apple-system, sans-serif; }
.kairos-toggle {
  width: 56px; height: 56px; border-radius: 50%;
  background: linear-gradient(135deg, #1e40af, #7c3aed);
  border: none; cursor: pointer; display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 20px rgba(30,64,175,0.4);
  transition: transform 0.2s, box-shadow 0.2s; color: white; font-size: 24px;
}
.kairos-toggle:hover { transform: scale(1.05); box-shadow: 0 6px 28px rgba(30,64,175,0.6); }
.kairos-chat {
  position: absolute; bottom: 68px; right: 0; width: 380px; height: 560px;
  background: var(--bg); border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px; display: none; flex-direction: column; overflow: hidden;
  box-shadow: 0 8px 40px rgba(0,0,0,0.5); backdrop-filter: blur(24px);
}
.kairos-chat.open { display: flex; }
.kairos-header {
  padding: 14px 16px; display: flex; align-items: center; gap: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.kairos-avatar {
  width: 32px; height: 32px; border-radius: 50%;
  background: linear-gradient(135deg, #1e40af, #7c3aed);
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: bold; color: white;
}
.kairos-title { color: #f1f5f9; font-size: 14px; font-weight: 600; flex: 1; }
.kairos-status {
  width: 8px; height: 8px; border-radius: 50%;
  background: #22c55e; display: inline-block;
}
.kairos-messages {
  flex: 1; overflow-y: auto; padding: 16px;
  display: flex; flex-direction: column; gap: 10px;
}
.kairos-msg {
  max-width: 88%; padding: 10px 14px; border-radius: 12px;
  font-size: 13px; line-height: 1.5; white-space: pre-wrap;
  animation: fadeIn 0.2s ease;
}
.kairos-msg.user {
  background: rgba(59,130,246,0.15); color: #f1f5f9;
  align-self: flex-end; border-bottom-right-radius: 4px;
}
.kairos-msg.assistant {
  background: rgba(255,255,255,0.04); color: #e2e8f0;
  align-self: flex-start; border-bottom-left-radius: 4px;
  border: 1px solid rgba(255,255,255,0.06);
}
.kairos-suggestions {
  display: flex; flex-wrap: wrap; gap: 6px; padding: 8px 16px;
}
.kairos-chip {
  padding: 6px 12px; border-radius: 16px; font-size: 11px;
  background: rgba(59,130,246,0.1); color: #93c5fd;
  border: 1px solid rgba(59,130,246,0.15); cursor: pointer;
  transition: all 0.2s; white-space: nowrap;
}
.kairos-chip:hover { background: rgba(59,130,246,0.2); border-color: rgba(59,130,246,0.3); }
.kairos-input-area {
  padding: 10px 12px; border-top: 1px solid rgba(255,255,255,0.08);
  display: flex; gap: 8px;
}
.kairos-input {
  flex: 1; padding: 10px 14px; border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.04); color: #f1f5f9;
  font-size: 13px; outline: none;
}
.kairos-input:focus { border-color: var(--primary-light); }
.kairos-send {
  width: 40px; height: 40px; border-radius: 10px;
  background: linear-gradient(135deg, #1e40af, #7c3aed);
  border: none; cursor: pointer; color: white;
  display: flex; align-items: center; justify-content: center; font-size: 18px;
}
.kairos-send:disabled { opacity: 0.4; cursor: default; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
.kairos-typing {
  display: flex; gap: 4px; padding: 10px 14px;
  background: rgba(255,255,255,0.04); border-radius: 12px;
  align-self: flex-start; border: 1px solid rgba(255,255,255,0.06);
}
.kairos-typing span {
  width: 6px; height: 6px; border-radius: 50%;
  background: #3b82f6; animation: typingDot 1.4s infinite;
}
.kairos-typing span:nth-child(2) { animation-delay: 0.2s; }
.kairos-typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes typingDot { 0%,60%,100% { opacity: 0.3; } 30% { opacity: 1; } }
</style>
<div class="kairos-widget">
  <button class="kairos-toggle" id="kairosToggle">✦</button>
  <div class="kairos-chat" id="kairosChat">
    <div class="kairos-header">
      <div class="kairos-avatar">K</div>
      <span class="kairos-title">Kairos Assistente</span>
      <span class="kairos-status"></span>
    </div>
    <div class="kairos-suggestions" id="kairosSuggestions">
      ${suggestions.map(s => `<span class="kairos-chip">${s}</span>`).join("")}
    </div>
    <div class="kairos-messages" id="kairosMessages"></div>
    <div class="kairos-input-area">
      <input class="kairos-input" id="kairosInput" placeholder="Digite sua mensagem..." />
      <button class="kairos-send" id="kairosSend">↑</button>
    </div>
  </div>
</div>
`

    const toggle = shadow.getElementById("kairosToggle")
    const chat = shadow.getElementById("kairosChat")
    const messages = shadow.getElementById("kairosMessages")
    const suggestionsEl = shadow.getElementById("kairosSuggestions")
    const input = shadow.getElementById("kairosInput")
    const sendBtn = shadow.getElementById("kairosSend")
    let isOpen = false
    let convId = null

    toggle.onclick = () => {
      isOpen = !isOpen
      chat.classList.toggle("open", isOpen)
      if (isOpen) input.focus()
    }

    const addMsg = (role, content) => {
      const div = document.createElement("div")
      div.className = `kairos-msg ${role}`
      div.textContent = content
      messages.appendChild(div)
      messages.scrollTop = messages.scrollHeight
    }

    const showTyping = () => {
      const div = document.createElement("div")
      div.className = "kairos-typing"
      div.id = "kairosTyping"
      div.innerHTML = "<span></span><span></span><span></span>"
      messages.appendChild(div)
      messages.scrollTop = messages.scrollHeight
    }

    const hideTyping = () => {
      const el = shadow.getElementById("kairosTyping")
      if (el) el.remove()
    }

    const handleSend = async (textOverride) => {
      const text = (textOverride || input.value).trim()
      if (!text || !client.online) return
      input.value = ""
      suggestionsEl.style.display = "none"
      addMsg("user", text)
      showTyping()
      sendBtn.disabled = true
      try {
        addMsg("assistant", "")
        hideTyping()
        showTyping()
        const lastMsg = messages.lastChild
        let responseText = ""
        await client.sendMessageStream(text, convId, (chunk) => {
          if (lastMsg && lastMsg.className && lastMsg.className.includes("kairos-msg assistant")) {
            responseText += chunk
            lastMsg.textContent = responseText
            messages.scrollTop = messages.scrollHeight
          }
        })
        hideTyping()
        const res = await client.sendMessage(text, convId)
        convId = res.conversation_id
      } catch (e) {
        hideTyping()
        addMsg("assistant", "Erro ao conectar com o servidor.")
      }
      sendBtn.disabled = false
    }

    sendBtn.onclick = () => handleSend()
    input.onkeydown = (e) => { if (e.key === "Enter") handleSend() }

    shadow.querySelectorAll(".kairos-chip").forEach(chip => {
      chip.onclick = () => handleSend(chip.textContent)
    })
  }

  global.Kairos = {
    client: null,
    initialize(config) {
      this.client = new KairosClient(config)
      return this.client
    },
    context: {
      async register(appInfo) {
        if (!global.Kairos.client) throw new Error("Kairos not initialized. Call Kairos.initialize() first.")
        await global.Kairos.client.registerContext(
          appInfo.app || global.Kairos.client.appName,
          appInfo.modulos || [],
          appInfo.context || ""
        )
        if (appInfo.usuario) {
          await global.Kairos.client.registerSession(
            appInfo.usuario,
            appInfo.usuario,
            appInfo.email || `${appInfo.usuario}@app.local`,
            appInfo.permissao || "member",
            appInfo.modulos || [],
            appInfo.departamentos || []
          )
        }
      }
    },
    renderWidget(containerId, options) {
      if (!this.client) throw new Error("Kairos not initialized. Call Kairos.initialize() first.")
      renderWidget(this.client, containerId, options || {})
    },
    renderChat(containerId) {
      this.renderWidget(containerId, {})
    },
  }

  global.KairosSDK = KairosClient
})(typeof window !== "undefined" ? window : this)
