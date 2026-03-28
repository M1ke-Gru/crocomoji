from app.schemas.player import PlayerCreate, PlayerIdentifier
from app.state.room import Room


class Main:
    def __init__(self) -> None:
        self.rooms: dict[str, Room]

    def create_room(self, player: PlayerCreate) -> PlayerIdentifier:
        self.rooms[player.room_name] = Room(name=player.room_name)
        identifier: PlayerIdentifier = self.rooms[player.room_name].add_player(player)
        return identifier

    def add_player(self, player: PlayerCreate) -> PlayerIdentifier:
        room = self.rooms[player.room_name]
        if not room:
            raise Exception(f"Room {room.name} does not exist.")
        identifier: PlayerIdentifier = room.add_player(player)
        return identifier

    def player_leaves_room(self, player_id: int, room_name: str):
        room = self.rooms[room_name]
        if not room:
            raise Exception(f"Room {room.name} does not exist.")
        room.players.pop(player_id)
        if room.players == {}:
            self.rooms.pop(room_name)
