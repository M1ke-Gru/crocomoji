from datetime import datetime
from ..phases import GamePhase
from .response import Response


class Game:
    def __init__(self, story_blocks: list[str], turn_order: list[str]):
        if not story_blocks:
            raise ValueError("Story blocks are required.")

        if not turn_order:
            raise ValueError("Turn order is required.")

        self.story_blocks = story_blocks
        self.turn_order = turn_order
        self.current_round_idx = 0
        self.phase = GamePhase.EMOJI_CLUE

        self.current_emojis: str = ""
        self.emoji_history: list[dict] = []
        self.responses: list[Response] = []
        self.selected_response_id: str | None = None
        self.final_response_id: str | None = None
        self.ai_similarity_score: float | None = None
        self.hits_remaining: int = 3

        self.started_at = datetime.utcnow()
        self.completed_at = None

    @property
    def current_sentence(self) -> str:
        return self.story_blocks[self.current_round_idx]

    @property
    def narrator_id(self) -> str:
        return self.turn_order[self.current_round_idx % len(self.turn_order)]

    def submit_emoji(self, player_id: str, emojis: str) -> None:
        if player_id != self.narrator_id:
            raise ValueError("Only the narrator can submit emoji clues.")

        if self.phase not in [GamePhase.EMOJI_CLUE, GamePhase.REFINEMENT]:
            raise ValueError("Emoji clues cannot be submitted in this phase.")

        self.current_emojis = emojis
        self.emoji_history.append(
            {
                "emojis": emojis,
                "player_id": player_id,
                "round_idx": self.current_round_idx,
                "timestamp": datetime.utcnow(),
            }
        )

    def submit_guess(self, player_id: str, text: str) -> None:
        if player_id == self.narrator_id:
            raise ValueError("Narrator cannot submit guesses.")

        if self.phase not in [GamePhase.GUESSING, GamePhase.REFINEMENT]:
            raise ValueError("Guesses cannot be submitted in this phase.")

        response = Response(player_id=player_id, text=text)
        self.responses.append(response)

    def set_selected_response(self, player_id: str, response_id: str) -> None:
        if player_id != self.narrator_id:
            raise ValueError("Only the narrator can select a response.")

        if self.phase != GamePhase.NARRATOR_SELECTING:
            raise ValueError(
                "Responses can only be selected in narrator selecting phase."
            )

        found = False
        for response in self.responses:
            if response.id == response_id:
                response.select()
                self.selected_response_id = response.id
                found = True
            else:
                response.unselect()

        if not found:
            raise ValueError("Response not found.")

    def set_final_response(self, player_id: str, response_id: str) -> None:
        if player_id != self.narrator_id:
            raise ValueError("Only the narrator can choose the final response.")

        if self.phase != GamePhase.FINAL_SUBMISSION:
            raise ValueError(
                "Final response can only be chosen in final submission phase."
            )

        for response in self.responses:
            if response.id == response_id:
                self.final_response_id = response.id
                return

        raise ValueError("Response not found.")

    def set_ai_score(self, score: float) -> None:
        if not 0 <= score <= 1:
            raise ValueError("AI similarity score must be between 0 and 1.")

        self.ai_similarity_score = score

    def lose_hit(self) -> None:
        if self.hits_remaining > 0:
            self.hits_remaining -= 1

    def advance_round(self) -> None:
        if self.current_round_idx + 1 >= len(self.story_blocks):
            self.phase = GamePhase.GAME_COMPLETE
            self.completed_at = datetime.utcnow()
            return

        self.current_round_idx += 1
        self.phase = GamePhase.EMOJI_CLUE
        self.current_emojis = ""
        self.emoji_history = []
        self.responses = []
        self.selected_response_id = None
        self.final_response_id = None
        self.ai_similarity_score = None
        self.hits_remaining = 3
