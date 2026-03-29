"""Integration tests for HTTP endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport

from main import app


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


class TestCreateRoom:
    async def test_creates_room(self, client):
        r = await client.post("/rooms", json={"room_name": "alpha"})
        assert r.status_code == 200
        assert r.json() == {"room_name": "alpha"}

    async def test_duplicate_room_is_400(self, client):
        await client.post("/rooms", json={"room_name": "alpha"})
        r = await client.post("/rooms", json={"room_name": "alpha"})
        assert r.status_code == 400

    async def test_missing_body_field_is_422(self, client):
        r = await client.post("/rooms", json={})
        assert r.status_code == 422


class TestListRooms:
    async def test_empty_list(self, client):
        r = await client.get("/rooms")
        assert r.status_code == 200
        assert r.json() == []

    async def test_returns_created_rooms(self, client):
        await client.post("/rooms", json={"room_name": "a"})
        await client.post("/rooms", json={"room_name": "b"})
        r = await client.get("/rooms")
        names = {room["name"] for room in r.json()}
        assert names == {"a", "b"}

    async def test_room_entry_shape(self, client):
        await client.post("/rooms", json={"room_name": "test"})
        rooms = (await client.get("/rooms")).json()
        room = next(r for r in rooms if r["name"] == "test")
        assert "player_count" in room
        assert "status" in room
        assert room["status"] == "waiting"


class TestGetRoom:
    async def test_returns_room_detail(self, client):
        await client.post("/rooms", json={"room_name": "test"})
        await client.post("/rooms/test/join", json={"display_name": "Alice"})
        r = await client.get("/rooms/test")
        assert r.status_code == 200
        body = r.json()
        assert body["name"] == "test"
        assert body["status"] == "waiting"
        assert len(body["players"]) == 1
        assert body["players"][0]["display_name"] == "Alice"

    async def test_missing_room_is_404(self, client):
        r = await client.get("/rooms/missing")
        assert r.status_code == 404

    async def test_player_has_stars_field(self, client):
        await client.post("/rooms", json={"room_name": "test"})
        await client.post("/rooms/test/join", json={"display_name": "Alice"})
        body = (await client.get("/rooms/test")).json()
        assert "stars" in body["players"][0]
        assert body["players"][0]["stars"] == 0.0


class TestJoinRoom:
    async def test_join_returns_player_id_and_room(self, client):
        await client.post("/rooms", json={"room_name": "test"})
        r = await client.post("/rooms/test/join", json={"display_name": "Alice"})
        assert r.status_code == 200
        body = r.json()
        assert "player_id" in body
        assert body["room_name"] == "test"
        assert len(body["player_id"]) == 8

    async def test_two_players_get_distinct_ids(self, client):
        await client.post("/rooms", json={"room_name": "test"})
        r1 = await client.post("/rooms/test/join", json={"display_name": "Alice"})
        r2 = await client.post("/rooms/test/join", json={"display_name": "Bob"})
        assert r1.json()["player_id"] != r2.json()["player_id"]

    async def test_join_missing_room_is_404(self, client):
        r = await client.post("/rooms/missing/join", json={"display_name": "Alice"})
        assert r.status_code == 404

    async def test_missing_display_name_is_422(self, client):
        await client.post("/rooms", json={"room_name": "test"})
        r = await client.post("/rooms/test/join", json={})
        assert r.status_code == 422


class TestHealth:
    async def test_health(self, client):
        r = await client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"


class TestWSActions:
    async def test_actions_endpoint(self, client):
        r = await client.get("/ws/actions")
        assert r.status_code == 200
        actions = r.json()
        assert "start_game" in actions
        assert "submit_ending" in actions
        assert "submit_vote" in actions
