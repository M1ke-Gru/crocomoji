from models.game import Game
from models.round import Round


class ScoringController:
    def __init__(self, game: Game) -> None:
        self.game = game

    def award_round(self, round_: Round) -> list[dict]:
        """
        Scoring:
        - 1 star per vote received
        - +0.5 bonus star if ALL other players voted for you (unanimous)

        Returns a list of result dicts sorted by votes descending.
        """
        total_players = len(self.game.players)
        results = []

        for player_id, text in round_.submissions.items():
            votes_received = sum(1 for v in round_.votes.values() if v == player_id)
            stars_earned = float(votes_received)

            others_count = total_players - 1
            if others_count > 0 and votes_received == others_count:
                stars_earned += 0.5

            player = self.game.players.get(player_id)
            if player:
                player.stars += stars_earned

            display_name = self.game.players[player_id].display_name if player_id in self.game.players else "?"
            results.append({
                "player_id": player_id,
                "display_name": display_name,
                "text": text,
                "votes": votes_received,
                "stars_earned": stars_earned,
            })

        results.sort(key=lambda r: r["votes"], reverse=True)
        return results
