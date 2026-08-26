"""Unit tests for arena generation and buff stations (Milestone 3 Scope)."""

from terragent.arena import (
    ITEM_CAMPFIRE,
    ITEM_HEART_LANTERN,
    ITEM_SUNFLOWER,
    ITEM_WOOD_PLATFORM,
    ArenaBuilder,
    ArenaSpec,
)


def test_arena_builder_default_generation() -> None:
    """Test standard arena generation commands, dimensions, and buff items."""
    spec = ArenaSpec(
        layers=3,
        platform_length=100,
        layer_spacing=6,
        campfire_spacing=40,
        heart_lantern_spacing=40,
        sunflower_spacing=50,
    )
    builder = ArenaBuilder(spec)

    commands = builder.generate_arena_commands(origin_x=500, origin_y=200)
    assert len(commands) > 0

    item_ids = {c.item_id for c in commands}
    assert ITEM_WOOD_PLATFORM in item_ids
    assert ITEM_CAMPFIRE in item_ids
    assert ITEM_HEART_LANTERN in item_ids
    assert ITEM_SUNFLOWER in item_ids

    # Verify platform tile count: 3 layers * 100 tiles = 300 platform blocks
    platform_cmds = [c for c in commands if c.item_id == ITEM_WOOD_PLATFORM]
    assert len(platform_cmds) == 300


def test_arena_bounds_calculation() -> None:
    """Test arena bounding box calculation."""
    builder = ArenaBuilder(ArenaSpec(layers=4, platform_length=120, layer_spacing=5))
    min_x, min_y, max_x, max_y = builder.get_arena_bounds(origin_x=1000, origin_y=500)

    assert min_x == 1000 - 60  # 940
    assert max_x == 1000 + 60  # 1060
    assert min_y == 500 - (4 * 5)  # 480
    assert max_y == 500
