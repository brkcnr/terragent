"""Categorized chest storage and item indexer for TerrAgent (Milestone 2 Scope).

This module manages the organized chest repository, maps items to categories,
and generates safe deposit and withdrawal command routines.
"""

import logging
from enum import StrEnum

from terragent.memory import MemoryStore
from terragent.schemas import DepositChestCommand, InventorySlot, WithdrawChestCommand

logger = logging.getLogger(__name__)


class ItemCategory(StrEnum):
    """Standard categorized chest groups defined in TerrAgent specification (§6.4)."""

    ORES_BARS = "ores_bars"
    BLOCKS_WALLS = "blocks_walls"
    WEAPONS_TOOLS = "weapons_tools"
    ACCESSORIES_ARMOR = "accessories_armor"
    POTIONS_CONSUMABLES = "potions_consumables"
    SEEDS_PLANTS = "seeds_plants"
    BOSS_SUMMONS_TROPHIES = "boss_summons_trophies"
    MISC = "misc"


def categorize_item(item_id: int, item_name: str) -> ItemCategory:
    """Classify an item into one of the 8 canonical storage categories.

    Args:
        item_id: The in-game Terraria item ID.
        item_name: Name string of the item.

    Returns:
        ItemCategory: The mapped storage category.
    """
    name = item_name.lower().strip()

    # 1. Ores and Bars
    if any(k in name for k in ("ore", "bar", "nugget", "meteorite", "hellstone")):
        return ItemCategory.ORES_BARS

    # 2. Blocks and Walls
    block_keywords = (
        "block",
        "wall",
        "wood",
        "stone",
        "dirt",
        "sand",
        "mud",
        "clay",
        "glass",
        "brick",
        "platform",
    )
    if any(k in name for k in block_keywords):
        return ItemCategory.BLOCKS_WALLS

    # 3. Weapons and Tools
    weapon_keywords = (
        "sword",
        "pickaxe",
        "axe",
        "hammer",
        "bow",
        "arrow",
        "staff",
        "wand",
        "gun",
        "bullet",
        "blade",
        "dagger",
        "spear",
        "boomerang",
    )
    if any(k in name for k in weapon_keywords):
        return ItemCategory.WEAPONS_TOOLS

    # 4. Accessories and Armor
    acc_keywords = (
        "helmet",
        "breastplate",
        "greaves",
        "armor",
        "boots",
        "band",
        "ring",
        "shield",
        "necklace",
        "emblem",
        "shackle",
        "watch",
        "compass",
        "radar",
    )
    if any(k in name for k in acc_keywords):
        return ItemCategory.ACCESSORIES_ARMOR

    # 5. Potions and Consumables
    potion_keywords = (
        "potion",
        "flask",
        "soup",
        "food",
        "ale",
        "bottle of",
        "healing",
        "mana",
        "buff",
    )
    if any(k in name for k in potion_keywords):
        return ItemCategory.POTIONS_CONSUMABLES

    # 6. Seeds and Plants
    plant_keywords = (
        "seed",
        "acorn",
        "mushroom",
        "daybloom",
        "blinkroot",
        "moonglow",
        "waterleaf",
        "deathweed",
        "fireblossom",
        "shiverthorn",
        "herb",
    )
    if any(k in name for k in plant_keywords):
        return ItemCategory.SEEDS_PLANTS

    # 7. Boss Summons and Trophies
    summon_keywords = (
        "suspicious looking",
        "worm food",
        "bloody spine",
        "abeemination",
        "voodoo doll",
        "trophy",
        "relic",
        "treasure bag",
    )
    if any(k in name for k in summon_keywords):
        return ItemCategory.BOSS_SUMMONS_TROPHIES

    # 8. Misc Default
    return ItemCategory.MISC


class StorageManager:
    """Coordinates chest registrations, deposit runs, and withdrawals."""

    ALL_CATEGORIES: list[ItemCategory] = list(ItemCategory)

    def __init__(self, memory: MemoryStore) -> None:
        """Initialize StorageManager with persistent memory store.

        Args:
            memory: Active MemoryStore instance.
        """
        self.memory = memory

    def register_base_storage_hall(self, origin_x: int, origin_y: int) -> list[int]:
        """Register the 8 categorized chests at the base storage hall in a row.

        Each chest is placed 3 tiles apart.

        Args:
            origin_x: Starting tile coordinate X.
            origin_y: Floor tile coordinate Y.

        Returns:
            list[int]: IDs of registered chests.
        """
        registered_ids: list[int] = []
        for i, category in enumerate(self.ALL_CATEGORIES):
            tile_x = origin_x + i * 3
            tile_y = origin_y
            chest_id = self.memory.register_chest(
                tile_x=tile_x,
                tile_y=tile_y,
                category=category.value,
                label=f"Chest: {category.value.title()}",
            )
            registered_ids.append(chest_id)
        return registered_ids

    def plan_deposit(
        self,
        inventory: list[InventorySlot],
        protected_hotbar_slots: int = 5,
    ) -> list[DepositChestCommand]:
        """Generate deposit commands for inventory items into categorized chests.

        Items in protected hotbar slots (0 to protected_hotbar_slots - 1) are never deposited.

        Args:
            inventory: Current inventory slots.
            protected_hotbar_slots: Number of hotbar slots to keep safe from deposit.

        Returns:
            list[DepositChestCommand]: Sequence of deposit actions.
        """
        commands: list[DepositChestCommand] = []

        for item in inventory:
            # Skip hotbar or empty items
            if item.slot < protected_hotbar_slots or item.stack <= 0 or item.item_id <= 0:
                continue

            cat = categorize_item(item.item_id, item.name)
            chests = self.memory.get_chests_by_category(cat.value)

            if not chests:
                # Fallback to misc chest if dedicated category chest not yet placed
                chests = self.memory.get_chests_by_category(ItemCategory.MISC.value)

            if chests:
                target_chest = chests[0]
                commands.append(
                    DepositChestCommand(
                        chest_x=target_chest["tile_x"],
                        chest_y=target_chest["tile_y"],
                        inventory_slot=item.slot,
                    )
                )

        return commands

    def plan_withdrawal(
        self,
        item_name_or_id: str | int,
        count: int = 1,
    ) -> list[WithdrawChestCommand]:
        """Generate withdrawal commands to retrieve a specific item from chests.

        Args:
            item_name_or_id: Target item ID or name string.
            count: Quantity of items to withdraw.

        Returns:
            list[WithdrawChestCommand]: Sequence of withdrawal actions.
        """
        matches = self.memory.find_item_in_chests(item_name_or_id)
        commands: list[WithdrawChestCommand] = []

        remaining = count
        for match in matches:
            if remaining <= 0:
                break

            commands.append(
                WithdrawChestCommand(
                    chest_x=match["tile_x"],
                    chest_y=match["tile_y"],
                    chest_slot=match["slot"],
                )
            )
            remaining -= int(match["stack"])

        return commands
