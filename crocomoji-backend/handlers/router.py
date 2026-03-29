from typing import Callable
from pydantic import BaseModel


class WSRouter:
    def __init__(self) -> None:
        self.handlers: dict[str, tuple[Callable, type[BaseModel] | None]] = {}

    def action(self, schema: type[BaseModel] | None = None):
        def decorator(fn: Callable):
            name = fn.__name__.removeprefix("handle_")
            self.handlers[name] = (fn, schema)
            return fn
        return decorator

    async def dispatch(self, room, player, action: str, raw_data: dict):
        entry = self.handlers.get(action)
        if not entry:
            return {"error": f"unknown action: {action}"}
        handler, schema = entry
        data = schema.model_validate(raw_data) if schema else None
        return await handler(room, player, data)
