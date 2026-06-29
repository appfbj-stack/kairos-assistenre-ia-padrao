from typing import Optional, AsyncGenerator
from core.domain.interfaces.llm_port import LLMPort
import json
import httpx
import os


class OpenRouterLLM(LLMPort):
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        self.base_url = base_url or "https://openrouter.ai/api/v1"
        self._model = model or os.getenv("OPENROUTER_MODEL", "openrouter/auto")

    async def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://assistente.fbautomacao.space",
        }

    async def chat(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        tools: Optional[list[dict]] = None,
    ) -> dict:
        body = {"model": model or self._model, "messages": messages}
        if tools:
            body["tools"] = tools
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=await self._headers(),
                json=body,
            )
            resp.raise_for_status()
            return resp.json()

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
                f"{self.base_url}/chat/completions",
                headers=await self._headers(),
                json=body,
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            delta = data["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except (json.JSONDecodeError, KeyError):
                            continue
