from abc import ABC, abstractmethod
from typing import Optional, AsyncGenerator


class LLMPort(ABC):
    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        tools: Optional[list[dict]] = None,
    ) -> dict: ...

    @abstractmethod
    def chat_stream(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        tools: Optional[list[dict]] = None,
    ) -> AsyncGenerator[str, None]: ...
