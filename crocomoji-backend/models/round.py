from typing import Literal
from pydantic import BaseModel, Field


class Round(BaseModel):
    index: int
    setup: str
    delivery: str = ""
    phase: Literal["submitting", "voting", "reveal"] = "submitting"
    submissions: dict[str, str] = Field(default_factory=dict)  # player_id → punchline text
    votes: dict[str, str] = Field(default_factory=dict)        # voter_id → voted_for_id
