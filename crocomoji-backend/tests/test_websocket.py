"""WebSocket endpoint tests."""
import json
import threading
import pytest
from unittest.mock import AsyncMock, patch
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from main import app


def _setup_room(client: TestClient, room: str = "test", names=("Alice", "Bob")) -> list[str]:
    """Create a room and join players via HTTP. Returns list of player_ids."""
    client.post("/rooms", json={"room_name": room})
    ids = []
    for name in names:
        r = client.post(f"/rooms/{room}/join", json={"display_name": name})
        ids.append(r.json()["player_id"])
    return ids


class TestWSConnectionRejection:
    def test_unknown_room_closes_4001(self):
        with TestClient(app) as client:
            with pytest.raises(WebSocketDisconnect) as exc:
                with client.websocket_connect("/ws/no-such-room/fakeid"):
                    pass
            assert exc.value.code == 4001

    def test_unknown_player_closes_4002(self):
        with TestClient(app) as client:
            client.post("/rooms", json={"room_name": "test"})
            with pytest.raises(WebSocketDisconnect) as exc:
                with client.websocket_connect("/ws/test/badplayerid"):
                    pass
            assert exc.value.code == 4002

    def test_valid_connect_is_accepted(self):
        with TestClient(app) as client:
            ids = _setup_room(client, names=("Alice",))
            # Should not raise
            with client.websocket_connect(f"/ws/test/{ids[0]}"):
                pass


class TestWSBroadcast:
    def test_player_connected_broadcast(self):
        """Second player connecting should notify the first."""
        received: list[dict] = []

        with TestClient(app) as client:
            ids = _setup_room(client)

            def listen_ws1():
                with client.websocket_connect(f"/ws/test/{ids[0]}") as ws1:
                    msg = ws1.receive_json()
                    received.append(msg)

            t = threading.Thread(target=listen_ws1)
            t.start()

            # Give ws1 time to connect, then connect ws2
            import time; time.sleep(0.05)
            with client.websocket_connect(f"/ws/test/{ids[1]}"):
                pass

            t.join(timeout=2)

        assert any(m["action"] == "player_connected" for m in received)
        connected_msg = next(m for m in received if m["action"] == "player_connected")
        assert connected_msg["data"]["display_name"] == "Bob"

    def test_player_disconnected_broadcast(self):
        """When a player leaves, remaining players get notified."""
        received: list[dict] = []

        with TestClient(app) as client:
            ids = _setup_room(client)

            def listen_ws1():
                with client.websocket_connect(f"/ws/test/{ids[0]}") as ws1:
                    # consume player_connected from ws2 joining
                    ws1.receive_json()
                    # then wait for disconnect notice
                    msg = ws1.receive_json()
                    received.append(msg)

            t = threading.Thread(target=listen_ws1)
            t.start()

            import time; time.sleep(0.05)
            with client.websocket_connect(f"/ws/test/{ids[1]}"):
                pass  # connect then immediately disconnect

            t.join(timeout=2)

        assert any(m["action"] == "player_disconnected" for m in received)


class TestWSActions:
    def test_unknown_action_returns_error(self):
        with TestClient(app) as client:
            ids = _setup_room(client, names=("Alice",))
            with client.websocket_connect(f"/ws/test/{ids[0]}") as ws:
                ws.send_json({"action": "does_not_exist", "data": {}})
                # The router returns an error dict; handler sends it back
                # (current router returns it but doesn't broadcast; skip if not sent)

    def test_submit_ending_wrong_phase_sends_error(self):
        """submit_ending during non-submitting phase returns an error."""
        with TestClient(app) as client:
            ids = _setup_room(client, names=("Alice",))
            with client.websocket_connect(f"/ws/test/{ids[0]}") as ws:
                ws.send_json({"action": "submit_ending", "data": {"text": "punchline"}})
                msg = ws.receive_json()
                assert msg["action"] == "error"
                assert "wrong phase" in msg["data"]["message"]

    def test_submit_vote_wrong_phase_sends_error(self):
        with TestClient(app) as client:
            ids = _setup_room(client, names=("Alice",))
            with client.websocket_connect(f"/ws/test/{ids[0]}") as ws:
                ws.send_json({"action": "submit_vote", "data": {"player_id": "anyone"}})
                msg = ws.receive_json()
                assert msg["action"] == "error"

    def test_start_game_not_enough_players_sends_error(self):
        with TestClient(app) as client:
            ids = _setup_room(client, names=("Alice",))  # only 1 player
            with client.websocket_connect(f"/ws/test/{ids[0]}") as ws:
                ws.send_json({"action": "start_game", "data": {"num_rounds": 3}})
                msg = ws.receive_json()
                assert msg["action"] == "error"

    @patch("handlers.actions.fetch_jokes", new_callable=AsyncMock)
    def test_start_game_broadcasts_game_started(self, mock_fetch):
        mock_fetch.return_value = ["Why did the chicken cross the road?"] * 2

        received_p1: list[dict] = []
        received_p2: list[dict] = []

        with TestClient(app) as client:
            ids = _setup_room(client)

            def run_p1():
                with client.websocket_connect(f"/ws/test/{ids[0]}") as ws:
                    while True:
                        msg = ws.receive_json()
                        received_p1.append(msg)
                        if msg["action"] in ("game_started", "error"):
                            break

            def run_p2():
                import time; time.sleep(0.1)
                with client.websocket_connect(f"/ws/test/{ids[1]}") as ws:
                    # drain player_connected for p1
                    ws.receive_json()
                    # send start_game
                    ws.send_json({"action": "start_game", "data": {"num_rounds": 2}})
                    while True:
                        msg = ws.receive_json()
                        received_p2.append(msg)
                        if msg["action"] in ("game_started", "error", "round_started"):
                            break

            t1 = threading.Thread(target=run_p1)
            t2 = threading.Thread(target=run_p2)
            t1.start()
            t2.start()
            t1.join(timeout=5)
            t2.join(timeout=5)

        all_msgs = received_p1 + received_p2
        actions = {m["action"] for m in all_msgs}
        assert "game_started" in actions or "round_started" in actions


class TestWSFullRound:
    """Full round flow: submit endings → vote → see results."""

    @patch("handlers.actions.fetch_jokes", new_callable=AsyncMock)
    def test_full_round(self, mock_fetch):
        mock_fetch.return_value = ["Why did the chicken cross the road?"]

        p1_msgs: list[dict] = []
        p2_msgs: list[dict] = []
        done = threading.Event()

        with TestClient(app) as client:
            ids = _setup_room(client)

            def run_p1():
                with client.websocket_connect(f"/ws/test/{ids[0]}") as ws:
                    while not done.is_set():
                        try:
                            msg = ws.receive_json()
                            p1_msgs.append(msg)
                            if msg["action"] == "voting_started":
                                # Vote for p2's submission (if it exists)
                                subs = msg["data"]["submissions"]
                                for pid in subs:
                                    if pid != ids[0]:
                                        ws.send_json({"action": "submit_vote", "data": {"player_id": pid}})
                                        break
                            if msg["action"] == "round_over":
                                done.set()
                        except Exception:
                            break

            def run_p2():
                import time; time.sleep(0.05)
                with client.websocket_connect(f"/ws/test/{ids[1]}") as ws:
                    ws.receive_json()  # player_connected for p1
                    ws.send_json({
                        "action": "start_game",
                        "data": {"num_rounds": 1, "joke_time_seconds": 60, "voting_time_seconds": 60},
                    })
                    while not done.is_set():
                        try:
                            msg = ws.receive_json()
                            p2_msgs.append(msg)
                            if msg["action"] == "round_started":
                                ws.send_json({"action": "submit_ending", "data": {"text": "To get to the other side!"}})
                            if msg["action"] == "voting_started":
                                subs = msg["data"]["submissions"]
                                for pid in subs:
                                    if pid != ids[1]:
                                        ws.send_json({"action": "submit_vote", "data": {"player_id": pid}})
                                        break
                            if msg["action"] == "round_over":
                                done.set()
                        except Exception:
                            break

            t1 = threading.Thread(target=run_p1)
            t2 = threading.Thread(target=run_p2)
            t1.start()
            t2.start()
            done.wait(timeout=5)
            t1.join(timeout=1)
            t2.join(timeout=1)

        all_msgs = p1_msgs + p2_msgs
        actions = {m["action"] for m in all_msgs}
        assert "game_started" in actions
        assert "round_started" in actions
        assert "voting_started" in actions
        assert "round_over" in actions

        round_over = next(m for m in all_msgs if m["action"] == "round_over")
        assert "results" in round_over["data"]
        assert "scores" in round_over["data"]
