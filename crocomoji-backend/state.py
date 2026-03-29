import asyncio
from models.room import Room

rooms: dict[str, Room] = {}
room_timers: dict[str, asyncio.Task] = {}
