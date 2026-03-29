import asyncio
from typing import Any
from pydantic import BaseModel, ConfigDict, Field
from models.game import Game


class Room(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    game: Game = Field(default_factory=Game)
    queues: dict[str, Any] = Field(default_factory=dict)
