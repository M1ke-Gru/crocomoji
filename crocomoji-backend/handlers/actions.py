import asyncio

from handlers.router import ActionRouter
from models.messages import StartGame, SubmitEnding, SubmitVote
from models.round import Round
from controllers.game import GameController
from controllers.round import RoundController
from controllers.scoring import ScoringController
from services.broadcast import broadcast, send_to
from services.jokes import fetch_jokes
from state import room_timers

router = ActionRouter()


# ── Timer helpers ────────────────────────────────────────────────────────────

def _cancel_timer(room_name: str) -> None:
    task = room_timers.pop(room_name, None)
    if task and not task.done():
        task.cancel()


def _schedule(room_name: str, coro) -> None:
    _cancel_timer(room_name)
    room_timers[room_name] = asyncio.create_task(coro)


# ── Phase transitions ────────────────────────────────────────────────────────

async def _start_round(room) -> None:
    gc = GameController(room.game)
    round_ = gc.current_round
    if not round_:
        return

    await broadcast(room, "round_started", {
        "round_index": round_.index,
        "setup": round_.setup,
        "phase": "submitting",
        "joke_time_seconds": room.game.joke_time_seconds,
        "total_rounds": len(room.game.rounds),
    })

    _schedule(room.name, _submission_timer(room))


async def _submission_timer(room) -> None:
    await asyncio.sleep(room.game.joke_time_seconds)
    gc = GameController(room.game)
    round_ = gc.current_round
    if round_ and round_.phase == "submitting":
        await _start_voting(room)


async def _start_voting(room) -> None:
    gc = GameController(room.game)
    round_ = gc.current_round
    if not round_ or round_.phase != "submitting":
        return

    _cancel_timer(room.name)
    round_.phase = "voting"

    # If nobody submitted at all, skip straight to reveal
    if not round_.submissions:
        await _end_round(room)
        return

    submissions_payload = {
        pid: {"display_name": room.game.players[pid].display_name, "text": text}
        for pid, text in round_.submissions.items()
        if pid in room.game.players
    }

    await broadcast(room, "voting_started", {
        "submissions": submissions_payload,
        "voting_time_seconds": room.game.voting_time_seconds,
    })

    _schedule(room.name, _voting_timer(room))


async def _voting_timer(room) -> None:
    await asyncio.sleep(room.game.voting_time_seconds)
    gc = GameController(room.game)
    round_ = gc.current_round
    if round_ and round_.phase == "voting":
        await _end_round(room)


async def _end_round(room) -> None:
    _cancel_timer(room.name)
    gc = GameController(room.game)
    round_ = gc.current_round
    if not round_ or round_.phase == "reveal":
        return

    round_.phase = "reveal"
    sc = ScoringController(room.game)
    results = sc.award_round(round_)
    scores = {pid: p.stars for pid, p in room.game.players.items()}

    await broadcast(
        room,
        "round_over",
        {
            "results": results,
            "scores": scores,
            "actual_punchline": round_.delivery,
        },
    )

    # Brief pause then advance to next round
    _schedule(room.name, _advance_after_reveal(room))


async def _advance_after_reveal(room) -> None:
    await asyncio.sleep(5)
    gc = GameController(room.game)
    has_next = gc.next_round()
    if not has_next:
        scores = {pid: p.stars for pid, p in room.game.players.items()}
        await broadcast(room, "game_over", {"scores": scores})
    else:
        await _start_round(room)


# ── WS Action handlers ───────────────────────────────────────────────────────

@router.action(StartGame)
async def handle_start_game(room, player, data: StartGame):
    gc = GameController(room.game)
    if not gc.can_start():
        await send_to(room, player.id, "error", {"message": "cannot start game"})
        return

    room.game.joke_time_seconds = data.joke_time_seconds
    room.game.voting_time_seconds = data.voting_time_seconds
    room.game.status = "playing"
    for player in room.game.players.values():
        player.stars = 0

    jokes = await fetch_jokes(data.num_rounds)
    room.game.rounds = [
        Round(index=i, setup=j["setup"], delivery=j["delivery"])
        for i, j in enumerate(jokes)
    ]
    room.game.current_round_index = 0

    await broadcast(room, "game_started", {
        "num_rounds": len(room.game.rounds),
        "joke_time_seconds": data.joke_time_seconds,
        "voting_time_seconds": data.voting_time_seconds,
    })

    await _start_round(room)


@router.action(SubmitEnding)
async def handle_submit_ending(room, player, data: SubmitEnding):
    gc = GameController(room.game)
    round_ = gc.current_round
    if not round_ or round_.phase != "submitting":
        await send_to(room, player.id, "error", {"message": "wrong phase"})
        return

    rc = RoundController(round_)
    if not rc.add_submission(player.id, data.text):
        await send_to(room, player.id, "error", {"message": "already submitted"})
        return

    await broadcast(room, "player_submitted", {
        "player_id": player.id,
        "display_name": player.display_name,
        "submitted_count": len(round_.submissions),
        "total_players": len(room.game.players),
    })

    if rc.all_submitted(room.game.players):
        await _start_voting(room)


@router.action(SubmitVote)
async def handle_submit_vote(room, player, data: SubmitVote):
    gc = GameController(room.game)
    round_ = gc.current_round
    if not round_ or round_.phase != "voting":
        await send_to(room, player.id, "error", {"message": "wrong phase"})
        return

    rc = RoundController(round_)
    if not rc.add_vote(player.id, data.player_id):
        await send_to(room, player.id, "error", {"message": "invalid vote"})
        return

    await broadcast(room, "vote_received", {
        "voter_id": player.id,
        "voter_name": player.display_name,
        "voted_count": len(round_.votes),
    })

    if rc.all_voted(room.game.players):
        await _end_round(room)
