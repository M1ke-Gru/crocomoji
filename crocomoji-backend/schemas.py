from pydantic import BaseModel


# This one can be sent to the frontend
class PlayerPublic(BaseModel):
    points: int
    responses: list[int]  # responses are retrieved separately with these with id's
    name: str
    is_narrating: bool

    room_id: int


# This one is recieved from the frontend and used for internal logic
# Inherits parameters from PlayerBase
class PlayerWithId(PlayerPublic):
    id: int


class Room(BaseModel):
    id: int


class Game(BaseModel):
    id: int
    text: str
    current_narator_id: int
    best_response_id: int
    room_id: int


class Sentence(BaseModel):
    id: int
    points: int
    text: str
    game_id: int


class Response(BaseModel):
    id: int
    text: str
    player_id: int
    sentence_id: int
