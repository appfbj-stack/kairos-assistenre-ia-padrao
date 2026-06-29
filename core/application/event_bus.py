from typing import Any, Callable
from core.domain.entities.event import Event, EventType
from core.domain.interfaces.event_port import EventPort


class InMemoryEventBus(EventPort):
    def __init__(self):
        self._handlers: dict[str, list[Callable]] = {}

    async def publish(self, event: Event):
        import time
        event.timestamp = time.time()
        handlers = self._handlers.get(event.type.value, [])
        for handler in handlers:
            try:
                await handler(event) if handler.__class__.__name__ == "coroutine" else handler(event)
            except Exception as e:
                error_handlers = self._handlers.get(EventType.ERROR.value, [])
                for eh in error_handlers:
                    await eh(Event(EventType.ERROR, {"original": event.type.value, "error": str(e)}))

    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable):
        handlers = self._handlers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)
