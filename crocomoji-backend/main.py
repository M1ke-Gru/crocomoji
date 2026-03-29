from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from models.messages import CreateRoomRequest, JoinRequest, WSMessage
from controllers.lobby import LobbyController
from controllers.game import GameController
from handlers.actions import router as ws_router
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


@app.get("/ws/actions")
async def available_actions():
    return {
        name: schema.model_json_schema() if schema else None
        for name, (_, schema) in ws_router.handlers.items()
    }


@app.websocket("/ws/{room_name}/{player_id}")
async def websocket_endpoint(ws: WebSocket, room_name: str, player_id: str):
    ctrl = LobbyController(rooms)
    room = ctrl.get_room(room_name)
    if not room:
        await ws.close(code=4001)
        return

    gc = GameController(room.game)
    player = gc.get_player(player_id)
    if not player:
        await ws.close(code=4002)
        return

    await ws.accept()
    room.connections[player_id] = ws

    await broadcast(
        room,
        "player_connected",
        {"player_id": player.id, "display_name": player.display_name},
        exclude=player_id,
    )

    display_name = player.display_name
    try:
        async for raw in ws.iter_json():
            msg = WSMessage.model_validate(raw)
            await ws_router.dispatch(room, player, msg.action, msg.data)
    except WebSocketDisconnect:
        pass
    finally:
        room.connections.pop(player_id, None)
        if room.game.status == "waiting":
            ctrl.leave_room(player_id, room_name)
        await broadcast(
            room,
            "player_disconnected",
            {"player_id": player_id, "display_name": display_name},
        )
