from uuid import uuid4
from .game import Game
from .schemas import PlayerBase, PlayerWithId


class Room:
    def __init__(self, room_id: str, host_id: str):
        self.room_id = room_id
        self.host_id = host_id
        self.players: dict[str, PlayerWithId] = {}
        self.game: Game | None = None

    def add_player(self, player: PlayerBase) -> PlayerWithId:
        new_player = PlayerWithId(
            id=str(uuid4()),
            name=player.name,
        )

        self.players[new_player.id] = new_player
        return new_player

    def start_game(self, story_blocks: list[str]) -> None:
        if len(self.players) < 2:
            raise ValueError("At least 2 players are required to start.")

        turn_order = list(self.players.keys())
        self.game = Game(story_blocks=story_blocks, turn_order=turn_order)