from uuid import uuid4
from models.player import Player
from models.room import Room


class LobbyController:
    def __init__(self, rooms: dict[str, Room]) -> None:
        self.rooms = rooms

    def create_room(self, room_name: str) -> Room:
        room = Room(name=room_name)
        self.rooms[room_name] = room
        return room

    def join_room(self, room_name: str, display_name: str) -> Player:
        room = self.rooms.get(room_name)
        if not room:
            raise KeyError(f"Room '{room_name}' not found")
        player = Player(
            id=uuid4().hex[:8],
            display_name=display_name,
            order=len(room.game.players),
        )
        room.game.players[player.id] = player
        return player

    def leave_room(self, player_id: str, room_name: str) -> None:
        room = self.rooms.get(room_name)
        if not room:
            return
        room.game.players.pop(player_id, None)
        if not room.game.players:
            self.rooms.pop(room_name, None)

    def get_room(self, room_name: str) -> Room | None:
        return self.rooms.get(room_name)

    def list_rooms(self) -> list[dict]:
        return [
            {
                "name": room.name,
                "player_count": len(room.game.players),
                "status": room.game.status,
            }
            for room in self.rooms.values()
        ]
