from fastapi import APIRouter

player_router = APIRouter(prefix="/player")

@player_router.get("/{id}")
def get_player_data(id: int):
    return { "player": id }
