from uuid import uuid4


class Response:
    def __init__(self, player_id: str, text: str):
        self.id: str = str(uuid4())
        self.player_id = player_id
        self.text = text
        self.is_selected = False

    def select(self) -> None:
        self.is_selected = True

    def unselect(self) -> None:
        self.is_selected = False