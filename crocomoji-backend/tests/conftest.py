import pytest
import state as state_module


@pytest.fixture(autouse=True)
def clean_state():
    """Reset global in-memory state before each test."""
    state_module.rooms.clear()
    for task in list(state_module.room_timers.values()):
        if not task.done():
            task.cancel()
    state_module.room_timers.clear()
    yield
    state_module.rooms.clear()
    state_module.room_timers.clear()
