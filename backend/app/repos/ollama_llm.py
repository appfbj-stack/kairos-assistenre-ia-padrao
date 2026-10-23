from typing import Optional, AsyncGenerator
from core.domain.interfaces.llm_port import LLMPort
import json
import httpx
import os
import logging
import uuid

logger = logging.getLogger(__name__)


class OllamaLLM(LLMPort):
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
        self._model = model or os.getenv("OLLAMA_MODEL", "llama3.2:3b")

    def _to_openai_response(self, ollama_data: dict) -> dict:
        msg = ollama_data.get("message", {})
        content = msg.get("content", "")
        openai_msg = {"role": "assistant", "content": content}
        raw_tool_calls = msg.get("tool_calls")
        if raw_tool_calls:
            openai_tool_calls = []
            for tc in raw_tool_calls:
                fn = tc.get("function", {})
                args = fn.get("arguments", {})
                openai_tool_calls.append({
                    "id": f"call_{uuid.uuid4().hex[:12]}",
                    "type": "function",
                    "function": {
                        "name": fn.get("name", ""),
                        "arguments": json.dumps(args) if isinstance(args, dict) else args,
                    },
                })
            openai_msg["tool_calls"] = openai_tool_calls
        return {"choices": [{"message": openai_msg}]}

    async def chat(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        tools: Optional[list[dict]] = None,
    ) -> dict:
        actual_model = model or self._model
        body = {"model": actual_model, "messages": messages, "stream": False}
        if tools:
            body["tools"] = tools
        logger.info(f"OLLAMA: url={self.base_url} model={actual_model} msgs={len(messages)} tools={bool(tools)}")
        if tools:
            logger.info(f"OLLAMA: tools_count={len(tools)} tools={[t.get('function',{}).get('name','') for t in tools]}")
        async with httpx.AsyncClient(timeout=300) as client:
            resp = await client.post(
                f"{self.base_url}/api/chat",
                json=body,
            )
            logger.info(f"OLLAMA: status={resp.status_code} len={len(resp.text)}")
            if resp.status_code != 200:
                logger.error(f"OLLAMA: error body={resp.text[:500]}")
            data = resp.json()
            return self._to_openai_response(data)

    async def chat_stream(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        tools: Optional[list[dict]] = None,
    ) -> AsyncGenerator[str, None]:
        body = {"model": model or self._model, "messages": messages, "stream": True}
        if tools:
            body["tools"] = tools
        async with httpx.AsyncClient(timeout=300) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json=body,
            ) as resp:
                if resp.status_code != 200:
                    error_text = await resp.aread()
                    raise Exception(f"Ollama error {resp.status_code}: {error_text[:500]}")
                async for line in resp.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        chunk = json.loads(line)
                        content = chunk.get("message", {}).get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue
