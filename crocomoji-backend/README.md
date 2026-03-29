# Crocomoji Backend

FastAPI + WebSocket backend for a multiplayer joke-ending game.

## Requirements

- Python 3.12+
- `uv` (recommended) or `pip`

## Setup

From `crocomoji-backend/`:

```bash
cd /home/corti/crocomoji/crocomoji-backend
```

### Option A: `uv` (recommended)

```bash
uv sync
```

### Option B: `pip`

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run The Server

```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server URL: `http://localhost:8000`

## Verify It Works

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"healthy"}
```

## HTTP API Quick Start

### 1. Create a room

```bash
curl -X POST http://localhost:8000/rooms \
  -H "Content-Type: application/json" \
  -d '{"room_name":"fun-room"}'
```

### 2. Join room as player 1

```bash
curl -X POST http://localhost:8000/rooms/fun-room/join \
  -H "Content-Type: application/json" \
  -d '{"display_name":"Alice"}'
```

### 3. Join room as player 2

```bash
curl -X POST http://localhost:8000/rooms/fun-room/join \
  -H "Content-Type: application/json" \
  -d '{"display_name":"Bob"}'
```

### 4. Inspect room

```bash
curl http://localhost:8000/rooms/fun-room
```

## WebSocket

Connect to:

```text
ws://localhost:8000/ws/{room_name}/{player_id}
```

Message format:

```json
{
  "action": "start_game",
  "data": {
    "num_rounds": 5,
    "joke_time_seconds": 60,
    "voting_time_seconds": 30
  }
}
```

You can list all available WebSocket actions and payload schemas here:

```bash
curl http://localhost:8000/ws/actions
```

## Test

```bash
uv run pytest
```

## Notes

- In-memory state only: no database, game state resets when server restarts.
- Joke setups are fetched from JokeAPI with local fallback setups if external fetch fails.
