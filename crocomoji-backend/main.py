import asyncio
import json

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from models.messages import CreateRoomRequest, JoinRequest, ActionMessage
from controllers.lobby import LobbyController
from controllers.game import GameController
from handlers.actions import router as action_router
from services.broadcast import broadcast
from state import rooms

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/rooms")
async def create_room(req: CreateRoomRequest):
    ctrl = LobbyController(rooms)
    if req.room_name in rooms:
        raise HTTPException(400, f"Room '{req.room_name}' already exists")
    room = ctrl.create_room(req.room_name)
    return {"room_name": room.name}


@app.get("/rooms")
async def list_rooms():
    ctrl = LobbyController(rooms)
    return ctrl.list_rooms()


@app.get("/rooms/{name}")
async def get_room(name: str):
    ctrl = LobbyController(rooms)
    room = ctrl.get_room(name)
    if not room:
        raise HTTPException(404, f"Room '{name}' not found")
    players = [
        {"id": p.id, "display_name": p.display_name, "stars": p.stars}
        for p in room.game.players.values()
    ]
    return {"name": room.name, "players": players, "status": room.game.status}


@app.post("/rooms/{name}/join")
async def join_room(name: str, req: JoinRequest):
    ctrl = LobbyController(rooms)
    try:
        player = ctrl.join_room(name, req.display_name)
    except KeyError as e:
        raise HTTPException(404, str(e))
    return {"player_id": player.id, "room_name": name}


@app.get("/rooms/{name}/events/{player_id}")
async def sse_stream(request: Request, name: str, player_id: str):
    ctrl = LobbyController(rooms)
    room = ctrl.get_room(name)
    if not room:
        raise HTTPException(404, f"Room '{name}' not found")

    gc = GameController(room.game)
    player = gc.get_player(player_id)
    if not player:
        raise HTTPException(404, f"Player '{player_id}' not found")

    queue: asyncio.Queue = asyncio.Queue()
    room.queues[player_id] = queue

    # Send current room state immediately
    queue.put_nowait({
        "action": "room_sync",
        "data": {
            "players": [
                {"id": p.id, "display_name": p.display_name, "stars": p.stars}
                for p in room.game.players.values()
            ],
            "status": room.game.status,
        },
    })

    await broadcast(
        room,
        "player_connected",
        {"player_id": player.id, "display_name": player.display_name},
        exclude=player_id,
    )

    display_name = player.display_name

    async def generate():
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=1.0)
                    yield f"data: {json.dumps(message)}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            room.queues.pop(player_id, None)
            if room.game.status == "waiting":
                ctrl.leave_room(player_id, name)
            await broadcast(
                room,
                "player_disconnected",
                {"player_id": player_id, "display_name": display_name},
            )

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.post("/rooms/{name}/actions/{player_id}")
async def handle_action(name: str, player_id: str, msg: ActionMessage):
    ctrl = LobbyController(rooms)
    room = ctrl.get_room(name)
    if not room:
        raise HTTPException(404, f"Room '{name}' not found")

    gc = GameController(room.game)
    player = gc.get_player(player_id)
    if not player:
        raise HTTPException(404, f"Player '{player_id}' not found")

    await action_router.dispatch(room, player, msg.action, msg.data)
    return {"ok": True}
