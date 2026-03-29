from models.round import Round


class RoundController:
    def __init__(self, round_: Round) -> None:
        self.round = round_

    def add_submission(self, player_id: str, text: str) -> bool:
        """Add punchline. Returns False if player already submitted."""
        if player_id in self.round.submissions:
            return False
        self.round.submissions[player_id] = text
        return True

    def add_vote(self, voter_id: str, voted_for_id: str) -> bool:
        """Cast a vote. Returns False if invalid (already voted, self-vote, no such submission)."""
        if voter_id in self.round.votes:
            return False
        if voter_id == voted_for_id:
            return False
        if voted_for_id not in self.round.submissions:
            return False
        self.round.votes[voter_id] = voted_for_id
        return True

    def all_submitted(self, players: dict) -> bool:
        return all(pid in self.round.submissions for pid in players)

    def all_voted(self, players: dict) -> bool:
        """True when every player who can vote has voted."""
        for player_id in players:
            if self._can_vote(player_id):
                if player_id not in self.round.votes:
                    return False
        return True

    def _can_vote(self, player_id: str) -> bool:
        return any(pid != player_id for pid in self.round.submissions)
