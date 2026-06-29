import json
import httpx
from typing import AsyncGenerator
from app.config import settings


def format_tools(tools_defs: list[dict]) -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t.get("schema", {}),
            },
        }
        for t in tools_defs
    ]


class LLMService:
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.openrouter_api_key
        self.model = model or settings.openrouter_model
        self.base_url = settings.openrouter_base_url

    async def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://assistente.fbautomacao.space",
        }

    def _build_messages(self, history: list[dict], prompt: str, context: str = "") -> list[dict]:
        messages = []
        if context:
            messages.append({"role": "system", "content": context})
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": prompt})
        return messages

    async def chat(
        self, history: list[dict], prompt: str, context: str = "", tools: list[dict] = None
    ) -> dict:
        messages = self._build_messages(history, prompt, context)
        body = {"model": self.model, "messages": messages}
        if tools:
            body["tools"] = format_tools(tools)

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=await self._headers(),
                json=body,
            )
            resp.raise_for_status()
            return resp.json()

    async def chat_stream(
        self, history: list[dict], prompt: str, context: str = "", tools: list[dict] = None
    ) -> AsyncGenerator[str, None]:
        messages = self._build_messages(history, prompt, context)
        body = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }
        if tools:
            body["tools"] = format_tools(tools)

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
