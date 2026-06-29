from abc import ABC, abstractmethod
from core.domain.entities.event import Event


class EventPort(ABC):
    @abstractmethod
    async def publish(self, event: Event) -> None: ...

    @abstractmethod
    def subscribe(self, event_type: str, handler: callable) -> None: ...

    @abstractmethod
    def unsubscribe(self, event_type: str, handler: callable) -> None: ...
