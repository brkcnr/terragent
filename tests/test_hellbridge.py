"""Unit tests for Underworld Hellbridge builder (Milestone 4 Scope)."""

from terragent.arena import ITEM_CAMPFIRE, ITEM_HEART_LANTERN, ITEM_WOOD_PLATFORM
from terragent.hellbridge import HellbridgeBuilder, HellbridgeSpec
from terragent.schemas import BreakTileCommand, PlaceTileCommand


def test_hellbridge_generation_and_spacing() -> None:
    """Test runway generation across Underworld horizontal span."""
    spec = HellbridgeSpec(
        start_x=1000,
        end_x=1500,
        bridge_y=3200,
        campfire_spacing=50,
        heart_lantern_spacing=50,
    )
    builder = HellbridgeBuilder(spec)

    commands = builder.generate_hellbridge_commands()
    assert len(commands) > 0

    place_cmds = [c for c in commands if isinstance(c, PlaceTileCommand)]
    platform_cmds = [c for c in place_cmds if c.item_id == ITEM_WOOD_PLATFORM]
    campfire_cmds = [c for c in place_cmds if c.item_id == ITEM_CAMPFIRE]
    lantern_cmds = [c for c in place_cmds if c.item_id == ITEM_HEART_LANTERN]

    # 500 platform tiles
    assert len(platform_cmds) == 500
    assert len(campfire_cmds) > 0
    assert len(lantern_cmds) > 0


def test_hellbridge_obstacle_clearing() -> None:
    """Test that ruin obstacles in the player's path are broken."""
    spec = HellbridgeSpec(start_x=1000, end_x=2000, bridge_y=3200, clear_height=4)
    builder = HellbridgeBuilder(spec)

    # Obstacles: (1200, 3198) is in path, (1200, 3180) is too high above path
    known_obstacles = [(1200, 3198), (1200, 3180), (500, 3198)]
    commands = builder.generate_hellbridge_commands(known_obstacle_tiles=known_obstacles)

    break_cmds = [c for c in commands if isinstance(c, BreakTileCommand)]
    assert len(break_cmds) == 1
    assert break_cmds[0].tile_x == 1200
    assert break_cmds[0].tile_y == 3198
