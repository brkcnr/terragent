"""Hardmode Wings acquisition manager for TerrAgent (Milestone 5 Scope).

This module manages prerequisites, material verification, and crafting/purchasing
pathways for early Hardmode wings (Harpy Wings, Frozen Wings, Leaf Wings).
"""

import logging

logger = logging.getLogger(__name__)

# Wing Item IDs
ITEM_SOUL_OF_FLIGHT = 575
ITEM_GIANT_HARPY_FEATHER = 760
ITEM_FROST_CORE = 1300
ITEM_FEATHER = 320
ITEM_SOUL_OF_LIGHT = 520
ITEM_SOUL_OF_NIGHT = 521

ITEM_HARPY_WINGS = 761
ITEM_FROZEN_WINGS = 1305
ITEM_ANGEL_WINGS = 492
ITEM_DEMON_WINGS = 493
ITEM_LEAF_WINGS = 748

KNOWN_WING_IDS = {
    ITEM_HARPY_WINGS,
    ITEM_FROZEN_WINGS,
    ITEM_ANGEL_WINGS,
    ITEM_DEMON_WINGS,
    ITEM_LEAF_WINGS,
}


class WingsManager:
    """Evaluates wing crafting materials, purchase viability, and equipped status."""

    def is_wings_equipped(self, equipped_item_ids: set[int]) -> bool:
        """Check whether any recognised Hardmode wings are currently equipped.

        Args:
            equipped_item_ids: Set of equipped accessory and armor item IDs.

        Returns:
            bool: True if wings are detected.
        """
        return bool(equipped_item_ids & KNOWN_WING_IDS)

    def can_craft_harpy_wings(
        self,
        inventory_item_counts: dict[int, int],
    ) -> tuple[bool, str]:
        """Check if materials for Harpy Wings (20 Soul of Flight + Giant Harpy Feather) are present.

        Args:
            inventory_item_counts: Mapping of item ID to quantity.

        Returns:
            tuple[bool, str]: (can_craft, status_description)
        """
        souls = inventory_item_counts.get(ITEM_SOUL_OF_FLIGHT, 0)
        feather = inventory_item_counts.get(ITEM_GIANT_HARPY_FEATHER, 0)

        if souls >= 20 and feather >= 1:
            return True, "Ready to craft Harpy Wings at Mythril/Orichalcum Anvil."

        missing: list[str] = []
        if souls < 20:
            missing.append(f"{20 - souls} Soul of Flight")
        if feather < 1:
            missing.append("Giant Harpy Feather")

        return False, f"Missing materials: {', '.join(missing)}."

    def can_purchase_leaf_wings(
        self,
        total_coins: int,
        in_jungle_biome: bool,
        is_night: bool,
    ) -> tuple[bool, str]:
        """Check if player can purchase Leaf Wings from Witch Doctor.

        Requirements: 1 Platinum Coin (1,000,000 copper value), Witch Doctor in Jungle, Nighttime.

        Args:
            total_coins: Total money value in copper.
            in_jungle_biome: Whether Witch Doctor housing is located in Jungle.
            is_night: Whether it is currently in-game night.

        Returns:
            tuple[bool, str]: (can_purchase, status_description)
        """
        PLATINUM_COIN_VALUE = 1_000_000

        if not in_jungle_biome:
            return False, "Witch Doctor must be housed in the Jungle biome."
        if not is_night:
            return False, "Leaf Wings are only sold during nighttime."
        if total_coins < PLATINUM_COIN_VALUE:
            return False, f"Insufficient funds ({total_coins} / {PLATINUM_COIN_VALUE} copper)."

        return True, "Ready to purchase Leaf Wings from Witch Doctor."
