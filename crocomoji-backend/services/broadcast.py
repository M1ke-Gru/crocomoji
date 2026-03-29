import json
from models.room import Room


async def broadcast(room: Room, action: str, data: dict, exclude: str | None = None) -> None:
    message = json.dumps({"action": action, "data": data})
    for player_id, ws in list(room.connections.items()):
        if player_id != exclude:
            try:
                await ws.send_text(message)
            except Exception:
                pass


async def send_to(room: Room, player_id: str, action: str, data: dict) -> None:
    ws = room.connections.get(player_id)
    if ws:
        try:
            await ws.send_text(json.dumps({"action": action, "data": data}))
        except Exception:
            pass
