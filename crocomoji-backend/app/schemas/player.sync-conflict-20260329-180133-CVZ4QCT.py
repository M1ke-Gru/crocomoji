from pydantic import BaseModel, ConfigDict


class PlayerCreate(BaseModel):
    name: str
    emoji: str

    room_name: str
    model_config = ConfigDict(from_attributes=True)


# This one can be sent to the frontend
class PlayerPublic(PlayerCreate):
    points: int = 0
    responses: list[int] = []  # responses are retrieved separately with these with id's
    is_narrating: bool = False


class PlayerIdentifier(BaseModel):
    id: int
    room_name: str
