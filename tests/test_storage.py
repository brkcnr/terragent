"""Unit tests for categorized chest storage and item indexer (Milestone 2 Scope)."""

from terragent.memory import MemoryStore
from terragent.schemas import ChestItemSlot, InventorySlot
from terragent.storage import ItemCategory, StorageManager, categorize_item


def test_categorize_item_all_categories() -> None:
    """Test item classification into canonical 8 categories."""
    assert categorize_item(12, "Iron Ore") == ItemCategory.ORES_BARS
    assert categorize_item(19, "Gold Bar") == ItemCategory.ORES_BARS
    assert categorize_item(9, "Wood") == ItemCategory.BLOCKS_WALLS
    assert categorize_item(30, "Dirt Block") == ItemCategory.BLOCKS_WALLS
    assert categorize_item(3507, "Copper Shortsword") == ItemCategory.WEAPONS_TOOLS
    assert categorize_item(3509, "Copper Pickaxe") == ItemCategory.WEAPONS_TOOLS
    assert categorize_item(89, "Hermes Boots") == ItemCategory.ACCESSORIES_ARMOR
    assert categorize_item(188, "Healing Potion") == ItemCategory.POTIONS_CONSUMABLES
    assert categorize_item(309, "Blinkroot Seeds") == ItemCategory.SEEDS_PLANTS
    assert categorize_item(43, "Suspicious Looking Eye") == ItemCategory.BOSS_SUMMONS_TROPHIES
    assert categorize_item(73, "Silver Coin") == ItemCategory.MISC


def test_storage_manager_deposit_planning() -> None:
    """Test generating deposit commands for inventory items into categorized chests."""
    mem = MemoryStore(":memory:")
    storage = StorageManager(mem)

    # Register storage hall at (100, 50)
    chest_ids = storage.register_base_storage_hall(origin_x=100, origin_y=50)
    assert len(chest_ids) == 8

    # Inventory with hotbar items (0-4) and non-hotbar items (5+)
    inventory = [
        InventorySlot(slot=0, item_id=3507, name="Copper Shortsword", stack=1),
        InventorySlot(slot=1, item_id=3509, name="Copper Pickaxe", stack=1),
        InventorySlot(slot=5, item_id=12, name="Iron Ore", stack=50),
        InventorySlot(slot=6, item_id=9, name="Wood", stack=150),
        InventorySlot(slot=7, item_id=188, name="Healing Potion", stack=10),
    ]

    deposit_cmds = storage.plan_deposit(inventory, protected_hotbar_slots=5)
    assert len(deposit_cmds) == 3

    # Verify target chests
    ores_chest = mem.get_chests_by_category(ItemCategory.ORES_BARS.value)[0]
    blocks_chest = mem.get_chests_by_category(ItemCategory.BLOCKS_WALLS.value)[0]
    potions_chest = mem.get_chests_by_category(ItemCategory.POTIONS_CONSUMABLES.value)[0]

    assert deposit_cmds[0].inventory_slot == 5
    assert deposit_cmds[0].chest_x == ores_chest["tile_x"]

    assert deposit_cmds[1].inventory_slot == 6
    assert deposit_cmds[1].chest_x == blocks_chest["tile_x"]

    assert deposit_cmds[2].inventory_slot == 7
    assert deposit_cmds[2].chest_x == potions_chest["tile_x"]


def test_storage_manager_withdrawal_planning() -> None:
    """Test generating withdrawal commands for requested items."""
    mem = MemoryStore(":memory:")
    storage = StorageManager(mem)

    storage.register_base_storage_hall(origin_x=100, origin_y=50)
    ores_chest = mem.get_chests_by_category(ItemCategory.ORES_BARS.value)[0]

    # Populate ores chest with Iron Ore
    mem.update_chest_contents(
        tile_x=ores_chest["tile_x"],
        tile_y=ores_chest["tile_y"],
        items=[
            ChestItemSlot(slot=0, item_id=12, name="Iron Ore", stack=50),
            ChestItemSlot(slot=1, item_id=12, name="Iron Ore", stack=50),
        ],
    )

    # Withdraw 60 Iron Ore (should draw from slot 0 and slot 1)
    withdraw_cmds = storage.plan_withdrawal("Iron Ore", count=60)
    assert len(withdraw_cmds) == 2
    assert withdraw_cmds[0].chest_slot == 0
    assert withdraw_cmds[1].chest_slot == 1
