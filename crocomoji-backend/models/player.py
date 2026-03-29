from pydantic import BaseModel


class Player(BaseModel):
    id: str
    display_name: str
    order: int = 0
    stars: float = 0.0
