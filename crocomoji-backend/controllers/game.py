from uuid import uuid4
from models.game import Game
from models.player import Player
from models.round import Round


class GameController:
    def __init__(self, game: Game) -> None:
        self.game = game

    def add_player(self, display_name: str) -> Player:
        player = Player(
            id=uuid4().hex[:8],
            display_name=display_name,
            order=len(self.game.players),
        )
        self.game.players[player.id] = player
        return player

    def remove_player(self, player_id: str) -> None:
        self.game.players.pop(player_id, None)

    def get_player(self, player_id: str) -> Player | None:
        return self.game.players.get(player_id)

    @property
    def current_round(self) -> Round | None:
        if self.game.current_round_index < len(self.game.rounds):
            return self.game.rounds[self.game.current_round_index]
        return None

    def next_round(self) -> bool:
        self.game.current_round_index += 1
        if self.game.current_round_index >= len(self.game.rounds):
            self.game.status = "finished"
            return False
        return True

    def can_start(self) -> bool:
        return len(self.game.players) >= 3 and self.game.status in ("waiting", "finished")
