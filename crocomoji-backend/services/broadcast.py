import json
from models.room import Room


async def broadcast(room: Room, action: str, data: dict, exclude: str | None = None) -> None:
    message = {"action": action, "data": data}
    for player_id, queue in list(room.queues.items()):
        if player_id != exclude:
            queue.put_nowait(message)


async def send_to(room: Room, player_id: str, action: str, data: dict) -> None:
    queue = room.queues.get(player_id)
    if queue:
        queue.put_nowait({"action": action, "data": data})
