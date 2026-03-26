from enum import Enum
from .schemas import PlayerWithId, Response


class GamePhase(str, Enum):
    LOBBY = "lobby"
    STORY_READY = "story_ready"
    EMOJI_CLUE = "emoji_clue"
    GUESSING = "guessing"
    NARRATOR_SELECTING = "narrator_selecting"
    REFINEMENT = "refinement"
    FINAL_SUBMISSION = "final_submission"
    AI_SCORING = "ai_scoring"
    ROUND_COMPLETE = "round_complete"
    GAME_COMPLETE = "game_complete"


class Round:
    def __init__(self, index: int, sentence: str, narrator_id: str):
        self.index = index
        self.sentence = sentence
        self.narrator_id = narrator_id
        self.phase = GamePhase.EMOJI_CLUE
        self.cycle = 1
        self.emoji_history: list[str] = []
        self.responses: list[Response] = []
        self.selected_response_ids: list[str] = []
        self.final_response_id: str | None = None
        self.ai_similarity_score: float | None = None
        self.started_at = None
        self.completed_at = None

    def submit_emoji(self, player_id: str, emojis: str) -> None:
        if player_id != self.narrator_id:
            raise ValueError("Only the narrator can submit emoji clues.")

        self.emoji_history.append(emojis)

    def submit_guess(self, player_id: str, text: str) -> None:
        if player_id == self.narrator_id:
            raise ValueError("Narrator cannot submit guesses.")

        response = Response(
            player_id=player_id,
            text=text,
        )
        self.responses.append(response)

    def select_response(self, player_id: str, response_id: str) -> None:
        if player_id != self.narrator_id:
            raise ValueError("Only the narrator can select a response.")

        for response in self.responses:
            if response.id == response_id:
                self.selected_response_ids.append(response_id)
                return

        raise ValueError("Response not found.")


class Room:
    def __init__(self, room_id: str, host_id: str):
        self.room_id = room_id
        self.host_id = host_id
        self.players: dict[str, PlayerWithId] = {}
        self.story_blocks: list[str] = []
        self.rounds: list[Round] = []
        self.current_round_idx = 0
        self.phase = GamePhase.LOBBY
        self.turn_order: list[str] = []
        self.game_started = False
        self.game_finished = False

    @property
    def current_round(self) -> Round:
        return self.rounds[self.current_round_idx]

    def add_player(self, player: PlayerWithId) -> None:
        if self.game_started:
            raise ValueError("Cannot join after the game has started.")

        if player.id in self.players:
            raise ValueError("Player already exists.")

        self.players[player.id] = player
        self.turn_order.append(player.id)

    def start_game(self, story_blocks: list[str]) -> None:
        if len(self.players) < 2:
            raise ValueError("At least 2 players are required.")

        if not story_blocks:
            raise ValueError("Story blocks are required.")

        self.story_blocks = story_blocks
        self.rounds = []

        for i, sentence in enumerate(story_blocks):
            narrator_id = self.turn_order[i % len(self.turn_order)]
            self.rounds.append(Round(index=i, sentence=sentence, narrator_id=narrator_id))

        self.current_round_idx = 0
        self.phase = GamePhase.EMOJI_CLUE
        self.game_started = True
        self.game_finished = False

    def advance_round(self) -> None:
        if self.current_round_idx + 1 >= len(self.rounds):
            self.phase = GamePhase.GAME_COMPLETE
            self.game_finished = True
            return

        self.current_round_idx += 1
        self.phase = GamePhase.EMOJI_CLUE