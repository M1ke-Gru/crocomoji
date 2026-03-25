from .schemas import PlayerWithId, Sentence, Response


class Room:
    def __init__(self, room_id: str, host_id: str):
        self.room_id = room_id
        self.players: dict[str, PlayerWithId] = {}
        self.sentences: list[Sentence] = []
        self.current_sentence_idx: int = 0
        self.hits_remaining: int = 3
        self.responses: list[Response] = []
        self.selected_responses: list[Response] = []
        self.current_emojis: str = ""
        self.emojifier_idx: int = 0
        self.emojifier_queue: list[PlayerWithId] = []

    @property
    def narrator_id(self) -> PlayerWithId:
        return self.emojifier_queue[self.emojifier_idx]

    @property
    def current_sentence(self) -> Sentence:
        return self.sentences[self.current_sentence_idx]

    def add_player(self, player: PlayerWithId) -> None: ...
    def submit_emoji(self, player_id: str, emojis: str) -> None: ...
    def submit_guess(self, player_id: str, text: str) -> None: ...
    def select_response(self, player_id: str, response_id: str) -> None: ...
    def advance_round(self) -> None: ...
