"""Unit tests for Dungeon manager and Skeletron curse initiation (Milestone 4 Scope)."""

from terragent.dungeon import (
    ITEM_COBALT_SHIELD,
    ITEM_MURAMASA,
    ITEM_SHADOW_KEY,
    DungeonManager,
)
from terragent.schemas import GameState, PlayerState


def test_dungeon_curse_readiness_conditions() -> None:
    """Test Skeletron summoning criteria validation."""
    mgr = DungeonManager()

    strategy = {
        "readiness_criteria": {
            "min_hp": 240,
            "min_defense": 16,
        }
    }

    # Case 1: Daytime -> rejected
    day_state = GameState(
        protocol_version="1.0.0",
        timestamp=100.0,
        player=PlayerState(hp=300, max_hp=300, defense=20, x=100.0, y=100.0),
        is_night=False,
    )
    can_summon_day, msg_day = mgr.can_summon_skeletron(day_state, strategy)
    assert can_summon_day is False
    assert "nighttime" in msg_day

    # Case 2: Nighttime but low HP -> rejected
    low_hp_state = GameState(
        protocol_version="1.0.0",
        timestamp=100.0,
        player=PlayerState(hp=200, max_hp=300, defense=20, x=100.0, y=100.0),
        is_night=True,
    )
    can_summon_hp, msg_hp = mgr.can_summon_skeletron(low_hp_state, strategy)
    assert can_summon_hp is False
    assert "HP" in msg_hp

    # Case 3: Ready at night -> accepted
    ready_state = GameState(
        protocol_version="1.0.0",
        timestamp=100.0,
        player=PlayerState(hp=300, max_hp=300, defense=20, x=100.0, y=100.0),
        is_night=True,
    )
    can_summon, _ = mgr.can_summon_skeletron(ready_state, strategy)
    assert can_summon is True

    # Curse command generation
    cmd = mgr.generate_curse_command()
    assert cmd.action == "interact_npc"
    assert cmd.npc_name == "Old Man"


def test_dungeon_loot_evaluation() -> None:
    """Test evaluating collected essential dungeon progression artifacts."""
    mgr = DungeonManager()

    owned_items = {ITEM_COBALT_SHIELD, ITEM_SHADOW_KEY, ITEM_MURAMASA}
    loot_status = mgr.evaluate_dungeon_loot(owned_items)

    assert loot_status["Cobalt Shield"] is True
    assert loot_status["Shadow Key"] is True
    assert loot_status["Muramasa"] is True
    assert loot_status["Handgun"] is False
