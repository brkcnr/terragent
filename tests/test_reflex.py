"""Unit tests for Reflex engine (Milestone 1 Scope)."""

from terragent.config import ReflexConfig
from terragent.reflex import ReflexEngine
from terragent.schemas import GameState, InventorySlot, PlayerState


def create_sample_state(
    hp: int,
    max_hp: int = 100,
    x: float = 2500.0,
    y: float = 1200.0,
) -> GameState:
    """Helper to construct a GameState instance for testing."""
    return GameState(
        protocol_version="1.0.0",
        timestamp=1724678400.0,
        player=PlayerState(
            hp=hp,
            max_hp=max_hp,
            x=x,
            y=y,
            selected_slot=0,
            inventory=[
                InventorySlot(slot=0, item_id=3507, name="Copper Shortsword", stack=1),
            ],
        ),
    )


def test_reflex_idle_when_hp_healthy() -> None:
    """Test that reflex does not trigger retreat when HP is at or above threshold."""
    engine = ReflexEngine(ReflexConfig(low_hp_threshold=100))
    state = create_sample_state(hp=100)

    action = engine.process_tick(state)
    assert action is None


def test_reflex_retreat_triggered_on_low_hp() -> None:
    """Test that reflex triggers retreat when HP drops below threshold."""
    config = ReflexConfig(low_hp_threshold=80, safe_retreat_offset_x=-75.0)
    engine = ReflexEngine(config)

    state = create_sample_state(hp=79, x=2500.0, y=1200.0)
    action = engine.process_tick(state)

    assert action is not None
    assert action.action == "move_to"
    assert action.target_x == 2425.0  # 2500 - 75
    assert action.target_y == 1200.0
    assert action.duration_ms == 300
