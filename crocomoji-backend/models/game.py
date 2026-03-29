from pydantic import BaseModel, Field
from models.player import Player
from models.round import Round


class Game(BaseModel):
    players: dict[str, Player] = Field(default_factory=dict)
    rounds: list[Round] = Field(default_factory=list)
    current_round_index: int = 0
    status: str = "waiting"
    joke_time_seconds: int = 60
    voting_time_seconds: int = 30
