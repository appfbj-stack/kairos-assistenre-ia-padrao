"""
Kairós Multimodal Engine
Orchestrates text, voice, image, and document processing.
"""
import json
import base64
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("kairos.multimodal")


class MultimodalInput:
    def __init__(self):
        self.text: str = ""
        self.audio_base64: str = ""
        self.images: list = []
        self.documents: list = []
        self.conversation_id: str = ""
        self.app_slug: str = ""
        self.language: str = "pt-BR"


class MultimodalOutput:
    def __init__(self):
        self.text: str = ""
        self.audio_base64: str = ""
        self.images: list = []
        self.actions: list = []
        self.conversation_id: str = ""


class MultimodalEngine:
    def __init__(self, openrouter_key: str = "", voice_tts_key: str = "", voice_provider: str = "openai"):
        self.or_key = openrouter_key
        self.tts_key = voice_tts_key or openrouter_key
        self.voice_provider = voice_provider
        self._upload_dir = Path.home() / ".kairos" / "uploads"
        self._upload_dir.mkdir(parents=True, exist_ok=True)
        self._stt = None
        self._tts = None
        self._vision = None

    @property
    def stt(self):
        if self._stt is None:
            from kairos_voice.stt import STTEngine
            self._stt = STTEngine(self.or_key)
        return self._stt

    @property
    def tts(self):
        if self._tts is None:
            from kairos_voice.tts import TTSEngine
            self._tts = TTSEngine(self.tts_key, self.voice_provider)
        return self._tts

    @property
    def vision(self):
        if self._vision is None:
            from kairos_vision.analyzer import VisionAnalyzer
            self._vision = VisionAnalyzer(self.or_key)
        return self._vision

    def process_input(self, inp: MultimodalInput) -> MultimodalOutput:
        out = MultimodalOutput()
        text = inp.text

        if inp.audio_base64:
            audio_bytes = base64.b64decode(inp.audio_base64)
            stt_result = self.stt.transcribe_bytes(audio_bytes, "wav", inp.language)
            text = stt_result.get("text", text)
            logger.info(f"STT: '{text}'")

        if inp.images:
            img_descriptions = []
            for img_data in inp.images:
                prompt = "Descreva esta imagem. Se houver texto, extraia todo o texto visível."
                if text:
                    prompt = f"Considerando a pergunta: '{text}', analise esta imagem e responda."
                result = self.vision._analyze(img_data if ";" not in img_data else img_data, prompt)
                img_descriptions.append(result.get("description", ""))
            img_context = "\n".join([f"[Imagem {i+1}: {d}]" for i, d in enumerate(img_descriptions)])

            if text:
                text = f"{text}\n\n{img_context}"
            else:
                text = img_context

        if inp.documents:
            from kairos_vision.document_reader import DocumentReader
            reader = DocumentReader()
            doc_texts = []
            for doc_data in inp.documents:
                if doc_data.startswith("base64:"):
                    raw = base64.b64decode(doc_data[7:])
                    tmp_path = self._upload_dir / "tmp_doc"
                    tmp_path.write_bytes(raw)
                    result = reader.read(str(tmp_path))
                    doc_texts.append(result.get("text", ""))
                elif Path(doc_data).exists():
                    result = reader.read(doc_data)
                    doc_texts.append(result.get("text", ""))

            doc_context = "\n".join([f"[Documento {i+1}: {d[:2000]}]" for i, d in enumerate(doc_texts)])
            if text:
                text = f"{text}\n\nConteúdo dos documentos:\n{doc_context}"
            else:
                text = doc_context

        out.text = text
        out.conversation_id = inp.conversation_id
        return out

    def process_output(self, text: str, conversation_id: str = "", tts: bool = False) -> MultimodalOutput:
        out = MultimodalOutput()
        out.text = text
        out.conversation_id = conversation_id
        if tts and text:
            audio_result = self.tts.speak(text)
            if audio_result.get("audio"):
                out.audio_base64 = base64.b64encode(audio_result["audio"]).decode()
        return out

    def save_upload(self, file_bytes: bytes, filename: str) -> dict:
        path = self._upload_dir / filename
        path.write_bytes(file_bytes)
        return {"path": str(path), "size": len(file_bytes), "saved": True}
