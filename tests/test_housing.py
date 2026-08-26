"""Unit tests for housing templates and layout planner (Milestone 2 Scope)."""

from terragent.housing import (
    ITEM_BED,
    ITEM_TORCH,
    ITEM_WOOD_CHAIR,
    ITEM_WOOD_DOOR,
    ITEM_WOOD_TABLE,
    HousingManager,
    TileCategory,
    create_player_bedroom,
    create_standard_npc_room,
)
from terragent.memory import MemoryStore


def test_standard_npc_room_template() -> None:
    """Test standard 10x6 interior NPC room template dimensions and requirements."""
    tpl = create_standard_npc_room(10, 6)
    # Exterior dimensions: (10 + 2) x (6 + 2) = 12 x 8 = 96 total tiles
    assert tpl.width == 12
    assert tpl.height == 8

    # Must be within Terraria housing bounds (60 to 750 total tiles)
    total_tiles = tpl.width * tpl.height
    assert 60 <= total_tiles <= 750

    # Verify presence of essential components
    categories = {t.category for t in tpl.tiles}
    assert TileCategory.SOLID_BLOCK in categories
    assert TileCategory.BACKGROUND_WALL in categories
    assert TileCategory.DOOR in categories
    assert TileCategory.FLAT_SURFACE in categories
    assert TileCategory.COMFORT_ITEM in categories
    assert TileCategory.LIGHT_SOURCE in categories

    # Verify specific items
    item_ids = {t.item_id for t in tpl.tiles}
    assert ITEM_WOOD_DOOR in item_ids
    assert ITEM_WOOD_TABLE in item_ids
    assert ITEM_WOOD_CHAIR in item_ids
    assert ITEM_TORCH in item_ids


def test_player_bedroom_template() -> None:
    """Test player bedroom template contains bed for setting spawn."""
    tpl = create_player_bedroom(10, 6)
    assert tpl.width == 12
    assert tpl.height == 8

    item_ids = {t.item_id for t in tpl.tiles}
    assert ITEM_BED in item_ids
    assert ITEM_WOOD_DOOR in item_ids
    assert ITEM_TORCH in item_ids


def test_template_instantiation() -> None:
    """Test converting relative blueprint into absolute PlaceTileCommands."""
    tpl = create_standard_npc_room(10, 6)
    commands = tpl.instantiate(origin_x=100, origin_y=50)

    assert len(commands) == len(tpl.tiles)
    assert commands[0].tile_x >= 100
    assert commands[0].tile_y >= 50
    assert all(c.action == "place_tile" for c in commands)


def test_housing_manager_layout_planning() -> None:
    """Test HousingManager planning room layouts and check coordinates."""
    mem = MemoryStore(":memory:")
    mgr = HousingManager(mem)

    # First room is player bedroom
    x0, y0, tpl0 = mgr.plan_next_room(base_origin_x=200, base_origin_y=100, room_index=0)
    assert x0 == 200
    assert y0 == 100
    assert "bedroom" in tpl0.name

    # Second room is NPC room placed adjacent to bedroom
    x1, y1, tpl1 = mgr.plan_next_room(base_origin_x=200, base_origin_y=100, room_index=1)
    assert x1 == 200 + tpl0.width - 1
    assert y1 == 100
    assert "npc_room" in tpl1.name

    # Register built room and calculate check coordinate
    room_id = mgr.register_built_room("Merchant Room", x1, y1, tpl1)
    check_x, check_y = mgr.get_housing_check_coordinate(room_id)
    assert check_x == x1 + tpl1.width // 2
    assert check_y == y1 + tpl1.height // 2
