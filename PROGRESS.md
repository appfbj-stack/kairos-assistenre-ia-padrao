# Kairos Assistant - Progresso

## Sessão 2026-06-29 — Multimodal Frontend Complete

### O que foi feito
- **Pacotes renomeados e reinstalados**: `kairos-voice/src/` → `kairos_voice/`, `kairos-vision/src/` → `kairos_vision/` como pacotes pip instaláveis
- **Imports corrigidos**: `conversation.py`, `ocr.py`, `engine.py`, `multimodal.py` agora usam `from kairos_voice.xxx` (sem `src.`)
- **Backend imports OK**: `python -c "from app.main import app"` funciona sem erros, `MultimodalEngine` importável
- **ChatInput multimodal** (frontend):
  - Botão de microfone → grava áudio → `POST /api/multimodal/voice`
  - Botão de anexo → upload imagem → `POST /api/multimodal/vision` ou documento → `POST /api/multimodal/document`
  - Preview de arquivos anexados com remoção
  - Estado de gravação com `animate-pulse` / botão "Parar"
- **ChatMessage atualizado**: renderiza imagens inline + badges de áudio/documento
- **ChatInterface atualizado**: mostra avatar durante streaming, badges de capabilities (voz/imagem/documentos) na tela vazia
- **AvatarCanvas** sincroniza estados: `listening` (ondas), `thinking` (rotação), `speaking` (pulso máximo)
- **chatStore** com suporte a `attachments[]` por mensagem
- **api.ts** com `sendMultimodalVoice`, `sendMultimodalVision`, `sendMultimodalDocument`
- **TypeScript OK**: `npx tsc --noEmit` limpo, `next lint` sem warnings

### Próximos passos
1. ✅ **Falta**: Testar fluxo completo multimodal com backend rodando + microfone real no navegador
2. ✅ **Falta**: Tocar resposta TTS no frontend quando avatar estiver `speaking`
3. ✅ **Falta**: Adicionar `multimodal memory` (histórico de arquivos por tenant/user)
4. ✅ **Backlog**: Deploy Dokploy com variáveis multimodais (OPENROUTER_API_KEY, TTS_API_KEY, etc.)

### Estrutura atual
```
C:\Users\ferna\kairos-assistant\
├── backend/app/
│   ├── multimodal/engine.py       ← +MultimodalEngine (texto/áudio/imagem/documento)
│   ├── routes/multimodal.py       ← 5 endpoints multimodais
│   └── routes/agent_ws.py         ← WebSocket do Kairós Agent
├── src/
│   ├── components/chat/
│   │   ├── ChatInput.tsx          ← +microfone, +upload, +preview
│   │   ├── ChatInterface.tsx      ← +avatar streaming, +capabilities
│   │   └── ChatMessage.tsx        ← +attachments rendering
│   ├── components/avatar/
│   │   └── AvatarCanvas.tsx       ← estados idle/listening/thinking/speaking
│   ├── stores/
│   │   ├── chatStore.ts           ← +attachments por mensagem
│   │   └── uiStore.ts             ← avatarState
│   ├── lib/api.ts                 ← +sendMultimodalVoice/Vision/Document
C:\Users\ferna\kairos-voice\        ← pacote pip (STT/TTS/microfone/playback)
C:\Users\ferna\kairos-vision\       ← pacote pip (visão/OCR/documentos)
C:\Users\ferna\kairos-agent\        ← Kairós Agent (repositório independente)
```

### Decisões
- `kairos-voice` e `kairos-vision` como pacotes pip separados → instaláveis via `pip install -e .`
- Frontend acessa `POST /api/multimodal/voice` com FormData (Blob) → evita WebSocket complexo para áudio
- Anexos convertidos para base64 no frontend → enviados como FormData para o backend
- AvatarCanvas é canvas 2D animado (sem Three.js) para manter bundle leve
- Microfone usa `MediaRecorder` com `audio/webm` → transcodificado no backend (se necessário)
