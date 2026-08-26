"""Unit tests for SQLite persistent memory store (Milestone 2 Scope)."""

from terragent.memory import MemoryStore
from terragent.schemas import ChestItemSlot, TownNPC


def test_memory_room_lifecycle() -> None:
    """Test creating, querying, and updating housing rooms."""
    mem = MemoryStore(":memory:")

    room_id = mem.record_room(
        name="Merchant's House",
        origin_x=100,
        origin_y=80,
        width=12,
        height=8,
        is_valid=False,
        assigned_npc=None,
    )
    assert room_id == 1

    # Initially not valid
    valid_rooms = mem.get_valid_rooms()
    assert len(valid_rooms) == 0

    # Mark valid after bridge query check
    mem.update_room_validity(room_id, is_valid=True, assigned_npc="Merchant")
    valid_rooms = mem.get_valid_rooms()
    assert len(valid_rooms) == 1
    assert valid_rooms[0]["assigned_npc"] == "Merchant"
    assert valid_rooms[0]["is_valid"] == 1


def test_memory_npc_roster_sync() -> None:
    """Test synchronizing Town NPC roster and counting housed NPCs."""
    mem = MemoryStore(":memory:")

    npcs = [
        TownNPC(npc_type=22, name="Andrew", is_housed=True, room_id=1),
        TownNPC(npc_type=17, name="Alfred", is_housed=True, room_id=2),
        TownNPC(npc_type=18, name="Molly", is_housed=False, room_id=None),
    ]
    mem.sync_npc_roster(npcs)

    housed = mem.get_housed_npcs()
    assert len(housed) == 2
    assert mem.count_housed_npcs() == 2

    # Update Molly to housed
    npcs[2].is_housed = True
    npcs[2].room_id = 3
    mem.sync_npc_roster(npcs)
    assert mem.count_housed_npcs() == 3


def test_memory_chest_registration_and_indexing() -> None:
    """Test registering chests, updating items, and searching for items in chest index."""
    mem = MemoryStore(":memory:")

    chest_id = mem.register_chest(
        tile_x=120,
        tile_y=80,
        category="ores_bars",
        label="Chest: Ores & Bars",
    )
    assert chest_id == 1

    items = [
        ChestItemSlot(slot=0, item_id=12, name="Iron Ore", stack=99),
        ChestItemSlot(slot=1, item_id=19, name="Gold Bar", stack=25),
        ChestItemSlot(slot=2, item_id=0, name="", stack=0),  # Empty slot
    ]
    mem.update_chest_contents(tile_x=120, tile_y=80, items=items)

    chest_data = mem.get_chest_by_location(120, 80)
    assert chest_data is not None
    assert len(chest_data["items"]) == 2
    assert chest_data["items"][0]["item_name"] == "Iron Ore"

    # Search item by name
    matches = mem.find_item_in_chests("Iron Ore")
    assert len(matches) == 1
    assert matches[0]["stack"] == 99
    assert matches[0]["chest_id"] == chest_id

    # Search item by ID
    matches_id = mem.find_item_in_chests(19)
    assert len(matches_id) == 1
    assert matches_id[0]["item_name"] == "Gold Bar"


def test_memory_spawn_point() -> None:
    """Test recording and retrieving base spawn point."""
    mem = MemoryStore(":memory:")

    assert mem.get_spawn_point() is None

    mem.set_spawn_point(tile_x=125, tile_y=82)
    spawn = mem.get_spawn_point()
    assert spawn == (125, 82)
