from random import randint, shuffle
from app.state.game import Game
from app.schemas.player import PlayerCreate, PlayerIdentifier, PlayerPublic


class Room:
    def __init__(self, name: str):
        self.room_name: str = name
        self.players: dict[int, PlayerPublic] = {}
        self.game: Game | None = None

    def add_player(self, player: PlayerCreate) -> PlayerIdentifier:
        if self.game:
            raise Exception(
                f"Player cannot be added to the room {player.room_name} as they are currently playing."
            )

        new_player: PlayerPublic = PlayerPublic(**player.model_dump())
        player_id: int = randint(0, 2147483647)

        self.players[player_id] = new_player
        return PlayerIdentifier(id=player_id, room_name=new_player.room_name)

    async def start_game(self, story_blocks: list[str]) -> None:
        if len(self.players) < 2:
            raise ValueError("At least 2 players are required to start.")

        turn_order = shuffle(list(self.players.keys()))
        if turn_order:
            self.game = Game(story_blocks=story_blocks, turn_order=turn_order)
