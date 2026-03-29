from pydantic import BaseModel


# HTTP schemas
class CreateRoomRequest(BaseModel):
    room_name: str


class JoinRequest(BaseModel):
    display_name: str


# WebSocket schemas
class WSMessage(BaseModel):
    action: str
    data: dict = {}


class StartGame(BaseModel):
    num_rounds: int = 5
    joke_time_seconds: int = 60
    voting_time_seconds: int = 30


class SubmitEnding(BaseModel):
    text: str


class SubmitVote(BaseModel):
    player_id: str
