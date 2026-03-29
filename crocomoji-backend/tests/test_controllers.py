"""Unit tests for all controllers (no HTTP, no WebSocket)."""
import pytest

import state as state_module
from controllers.lobby import LobbyController
from controllers.game import GameController
from controllers.round import RoundController
from controllers.scoring import ScoringController
from models.game import Game
from models.player import Player
from models.round import Round


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_game(*display_names: str) -> Game:
    game = Game()
    gc = GameController(game)
    for name in display_names:
        gc.add_player(name)
    return game


def make_round(setup: str = "Why did the chicken cross the road?") -> Round:
    return Round(index=0, setup=setup)


# ── LobbyController ──────────────────────────────────────────────────────────

class TestLobbyController:
    def test_create_room(self):
        ctrl = LobbyController(state_module.rooms)
        room = ctrl.create_room("lobby1")
        assert room.name == "lobby1"
        assert "lobby1" in state_module.rooms

    def test_join_room_creates_player(self):
        ctrl = LobbyController(state_module.rooms)
        ctrl.create_room("lobby1")
        player = ctrl.join_room("lobby1", "Alice")
        assert player.display_name == "Alice"
        assert len(player.id) == 8
        assert player.order == 0

    def test_join_room_increments_order(self):
        ctrl = LobbyController(state_module.rooms)
        ctrl.create_room("lobby1")
        p1 = ctrl.join_room("lobby1", "Alice")
        p2 = ctrl.join_room("lobby1", "Bob")
        assert p1.order == 0
        assert p2.order == 1

    def test_join_nonexistent_room_raises(self):
        ctrl = LobbyController(state_module.rooms)
        with pytest.raises(KeyError):
            ctrl.join_room("nope", "Alice")

    def test_leave_room_removes_player(self):
        ctrl = LobbyController(state_module.rooms)
        ctrl.create_room("lobby1")
        player = ctrl.join_room("lobby1", "Alice")
        ctrl.join_room("lobby1", "Bob")

        ctrl.leave_room(player.id, "lobby1")
        room = ctrl.get_room("lobby1")
        assert player.id not in room.game.players

    def test_leave_room_deletes_empty_room(self):
        ctrl = LobbyController(state_module.rooms)
        ctrl.create_room("lobby1")
        player = ctrl.join_room("lobby1", "Alice")

        ctrl.leave_room(player.id, "lobby1")
        assert ctrl.get_room("lobby1") is None

    def test_leave_nonexistent_room_is_safe(self):
        ctrl = LobbyController(state_module.rooms)
        ctrl.leave_room("fakeid", "fakroom")  # should not raise

    def test_get_room_returns_none_for_missing(self):
        ctrl = LobbyController(state_module.rooms)
        assert ctrl.get_room("missing") is None

    def test_list_rooms(self):
        ctrl = LobbyController(state_module.rooms)
        ctrl.create_room("a")
        ctrl.create_room("b")
        ctrl.join_room("a", "Alice")
        listing = ctrl.list_rooms()
        names = {r["name"] for r in listing}
        assert names == {"a", "b"}
        a_entry = next(r for r in listing if r["name"] == "a")
        assert a_entry["player_count"] == 1
        assert a_entry["status"] == "waiting"


# ── GameController ────────────────────────────────────────────────────────────

class TestGameController:
    def test_can_start_requires_two_players(self):
        game = make_game("Alice")
        assert not GameController(game).can_start()

    def test_can_start_with_two_players(self):
        game = make_game("Alice", "Bob")
        assert GameController(game).can_start()

    def test_can_start_only_when_waiting(self):
        game = make_game("Alice", "Bob")
        game.status = "playing"
        assert not GameController(game).can_start()

    def test_add_player_stores_in_game(self):
        game = Game()
        gc = GameController(game)
        p = gc.add_player("Alice")
        assert p.id in game.players
        assert game.players[p.id].display_name == "Alice"

    def test_remove_player(self):
        game = make_game("Alice", "Bob")
        gc = GameController(game)
        ids = list(game.players)
        gc.remove_player(ids[0])
        assert ids[0] not in game.players

    def test_get_player_found_and_missing(self):
        game = make_game("Alice")
        gc = GameController(game)
        pid = list(game.players)[0]
        assert gc.get_player(pid) is not None
        assert gc.get_player("nope") is None

    def test_current_round_none_when_no_rounds(self):
        game = make_game("Alice", "Bob")
        assert GameController(game).current_round is None

    def test_current_round_returns_active_round(self):
        game = make_game("Alice", "Bob")
        game.rounds = [make_round(), make_round()]
        game.current_round_index = 1
        gc = GameController(game)
        assert gc.current_round is game.rounds[1]

    def test_next_round_advances_index(self):
        game = make_game("Alice", "Bob")
        game.rounds = [make_round(), make_round()]
        gc = GameController(game)
        result = gc.next_round()
        assert result is True
        assert game.current_round_index == 1

    def test_next_round_finishes_game(self):
        game = make_game("Alice", "Bob")
        game.rounds = [make_round()]
        gc = GameController(game)
        result = gc.next_round()
        assert result is False
        assert game.status == "finished"


# ── RoundController ───────────────────────────────────────────────────────────

class TestRoundController:
    def test_add_submission(self):
        rc = RoundController(make_round())
        assert rc.add_submission("p1", "punchline") is True
        assert rc.round.submissions["p1"] == "punchline"

    def test_add_submission_duplicate_rejected(self):
        rc = RoundController(make_round())
        rc.add_submission("p1", "first")
        assert rc.add_submission("p1", "second") is False
        assert rc.round.submissions["p1"] == "first"

    def test_all_submitted_true(self):
        game = make_game("Alice", "Bob")
        rc = RoundController(make_round())
        for pid in game.players:
            rc.add_submission(pid, "punchline")
        assert rc.all_submitted(game.players) is True

    def test_all_submitted_false(self):
        game = make_game("Alice", "Bob")
        rc = RoundController(make_round())
        pid = list(game.players)[0]
        rc.add_submission(pid, "only one")
        assert rc.all_submitted(game.players) is False

    def test_add_vote_success(self):
        game = make_game("Alice", "Bob")
        ids = list(game.players)
        rc = RoundController(make_round())
        rc.add_submission(ids[0], "punch A")
        rc.add_submission(ids[1], "punch B")
        assert rc.add_vote(ids[1], ids[0]) is True
        assert rc.round.votes[ids[1]] == ids[0]

    def test_add_vote_self_vote_rejected(self):
        game = make_game("Alice", "Bob")
        ids = list(game.players)
        rc = RoundController(make_round())
        rc.add_submission(ids[0], "punch")
        assert rc.add_vote(ids[0], ids[0]) is False

    def test_add_vote_duplicate_rejected(self):
        game = make_game("Alice", "Bob")
        ids = list(game.players)
        rc = RoundController(make_round())
        rc.add_submission(ids[0], "punch A")
        rc.add_submission(ids[1], "punch B")
        rc.add_vote(ids[1], ids[0])
        assert rc.add_vote(ids[1], ids[0]) is False

    def test_add_vote_for_nonsubmitter_rejected(self):
        game = make_game("Alice", "Bob", "Carol")
        ids = list(game.players)
        rc = RoundController(make_round())
        rc.add_submission(ids[0], "punch")
        # ids[2] (Carol) never submitted — can't vote for them
        assert rc.add_vote(ids[1], ids[2]) is False

    def test_all_voted_when_everyone_can_vote(self):
        game = make_game("Alice", "Bob")
        ids = list(game.players)
        rc = RoundController(make_round())
        rc.add_submission(ids[0], "A")
        rc.add_submission(ids[1], "B")
        rc.add_vote(ids[0], ids[1])
        rc.add_vote(ids[1], ids[0])
        assert rc.all_voted(game.players) is True

    def test_all_voted_false_when_pending(self):
        game = make_game("Alice", "Bob")
        ids = list(game.players)
        rc = RoundController(make_round())
        rc.add_submission(ids[0], "A")
        rc.add_submission(ids[1], "B")
        rc.add_vote(ids[0], ids[1])
        # Bob hasn't voted yet
        assert rc.all_voted(game.players) is False

    def test_all_voted_when_only_one_submission(self):
        """If only one person submitted, they can't vote (self-vote forbidden).
        Everyone else can vote for them. Once they all do, all_voted is True."""
        game = make_game("Alice", "Bob", "Carol")
        ids = list(game.players)
        rc = RoundController(make_round())
        rc.add_submission(ids[0], "only one")  # Alice submitted
        # Bob and Carol vote for Alice; Alice cannot vote
        rc.add_vote(ids[1], ids[0])
        rc.add_vote(ids[2], ids[0])
        assert rc.all_voted(game.players) is True

    def test_all_voted_true_when_no_submissions(self):
        """Nobody submitted → no eligible voters → vacuously all voted."""
        game = make_game("Alice", "Bob")
        rc = RoundController(make_round())
        assert rc.all_voted(game.players) is True


# ── ScoringController ─────────────────────────────────────────────────────────

class TestScoringController:
    def _setup(self, *names: str):
        game = make_game(*names)
        return game, ScoringController(game), list(game.players)

    def test_one_vote_gives_one_star(self):
        game, sc, ids = self._setup("Alice", "Bob")
        round_ = make_round()
        round_.submissions = {ids[0]: "punch A", ids[1]: "punch B"}
        round_.votes = {ids[1]: ids[0]}  # Bob votes Alice

        results = sc.award_round(round_)
        alice = next(r for r in results if r["player_id"] == ids[0])
        assert alice["votes"] == 1
        assert alice["stars_earned"] == 1.0
        assert game.players[ids[0]].stars == 1.0

    def test_zero_votes_gives_zero_stars(self):
        game, sc, ids = self._setup("Alice", "Bob")
        round_ = make_round()
        round_.submissions = {ids[0]: "punch A", ids[1]: "punch B"}
        round_.votes = {ids[0]: ids[1]}  # Alice votes Bob, nobody votes Alice

        results = sc.award_round(round_)
        alice = next(r for r in results if r["player_id"] == ids[0])
        assert alice["stars_earned"] == 0.0

    def test_unanimous_bonus(self):
        """All other players voted for Alice → +0.5 bonus."""
        game, sc, ids = self._setup("Alice", "Bob", "Carol")
        round_ = make_round()
        round_.submissions = {ids[0]: "A", ids[1]: "B", ids[2]: "C"}
        round_.votes = {
            ids[1]: ids[0],  # Bob → Alice
            ids[2]: ids[0],  # Carol → Alice
            ids[0]: ids[1],  # Alice → Bob
        }

        results = sc.award_round(round_)
        alice = next(r for r in results if r["player_id"] == ids[0])
        assert alice["votes"] == 2
        assert alice["stars_earned"] == 2.5  # 2 votes + 0.5 unanimous bonus

    def test_no_unanimous_bonus_when_not_all_voted_for(self):
        game, sc, ids = self._setup("Alice", "Bob", "Carol")
        round_ = make_round()
        round_.submissions = {ids[0]: "A", ids[1]: "B", ids[2]: "C"}
        round_.votes = {
            ids[1]: ids[0],  # Bob → Alice
            ids[0]: ids[1],  # Alice → Bob
            ids[2]: ids[1],  # Carol → Bob (not Alice)
        }

        results = sc.award_round(round_)
        alice = next(r for r in results if r["player_id"] == ids[0])
        assert alice["stars_earned"] == 1.0  # 1 vote, no bonus

    def test_results_sorted_by_votes_descending(self):
        game, sc, ids = self._setup("Alice", "Bob", "Carol")
        round_ = make_round()
        round_.submissions = {ids[0]: "A", ids[1]: "B", ids[2]: "C"}
        round_.votes = {
            ids[1]: ids[0],
            ids[2]: ids[0],
            ids[0]: ids[2],
        }

        results = sc.award_round(round_)
        assert results[0]["player_id"] == ids[0]  # Alice has most votes

    def test_stars_accumulate_across_rounds(self):
        game, sc, ids = self._setup("Alice", "Bob")
        for _ in range(3):
            r = make_round()
            r.submissions = {ids[0]: "A", ids[1]: "B"}
            r.votes = {ids[1]: ids[0]}
            sc.award_round(r)

        assert game.players[ids[0]].stars == 3.0

    def test_players_not_in_submissions_get_nothing(self):
        """A player who didn't submit doesn't appear in results."""
        game, sc, ids = self._setup("Alice", "Bob", "Carol")
        round_ = make_round()
        # Carol never submitted
        round_.submissions = {ids[0]: "A", ids[1]: "B"}
        round_.votes = {ids[0]: ids[1]}

        results = sc.award_round(round_)
        result_ids = {r["player_id"] for r in results}
        assert ids[2] not in result_ids
        assert game.players[ids[2]].stars == 0.0
