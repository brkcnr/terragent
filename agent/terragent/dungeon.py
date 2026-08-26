"""Dungeon exploration and Skeletron curse manager for TerrAgent (Milestone 4 Scope).

This module coordinates Old Man curse interactions at the Dungeon entrance,
verifies night summoning conditions, and tracks golden locked chest loot.
"""

import logging
from typing import Any

from terragent.schemas import GameState, InteractNPCCommand

logger = logging.getLogger(__name__)

# Essential Dungeon Loot Item IDs
ITEM_GOLDEN_KEY = 327
ITEM_SHADOW_KEY = 329
ITEM_COBALT_SHIELD = 156
ITEM_MURAMASA = 155
ITEM_HANDGUN = 164
ITEM_AQUA_SCEPTER = 157


class DungeonManager:
    """Manages Dungeon entry prerequisites, curse triggering, and loot tracking."""

    ESSENTIAL_DUNGEON_LOOT = {
        "Cobalt Shield": ITEM_COBALT_SHIELD,
        "Shadow Key": ITEM_SHADOW_KEY,
        "Muramasa": ITEM_MURAMASA,
        "Handgun": ITEM_HANDGUN,
        "Aqua Scepter": ITEM_AQUA_SCEPTER,
    }

    def can_summon_skeletron(
        self,
        game_state: GameState,
        skeletron_strategy: dict[str, Any],
    ) -> tuple[bool, str]:
        """Verify whether all conditions are met to trigger the Skeletron curse.

        Args:
            game_state: Live GameState snapshot.
            skeletron_strategy: Strategy definition from boss_strategies.yaml.

        Returns:
            tuple[bool, str]: (is_ready, rationale_message)
        """
        player = game_state.player
        readiness = skeletron_strategy.get("readiness_criteria", {})

        # 1. Verify nighttime condition
        if not game_state.is_night:
            return False, "Skeletron can only be summoned during nighttime (7:30 PM - 4:30 AM)."

        # 2. Check player HP
        min_hp = readiness.get("min_hp", 240)
        if player.hp < min_hp:
            return False, f"Player HP ({player.hp}) is below minimum requirement ({min_hp})."

        # 3. Check player defense
        min_def = readiness.get("min_defense", 16)
        if player.defense < min_def:
            return (
                False,
                f"Player defense ({player.defense}) is below minimum requirement ({min_def}).",
            )

        return True, "Ready to initiate Skeletron encounter."

    def generate_curse_command(self) -> InteractNPCCommand:
        """Generate action command to speak with Old Man and initiate Skeletron fight.

        Returns:
            InteractNPCCommand: Dialogue action targeting the Old Man.
        """
        logger.info("Generating Old Man curse interaction command to summon Skeletron.")
        return InteractNPCCommand(npc_name="Old Man", option_index=0)

    def evaluate_dungeon_loot(
        self,
        inventory_item_ids: set[int],
    ) -> dict[str, bool]:
        """Check which essential Dungeon progression items have been collected.

        Args:
            inventory_item_ids: Set of all item IDs currently owned in inventory/chests.

        Returns:
            dict[str, bool]: Status for each key dungeon artifact.
        """
        return {
            name: (item_id in inventory_item_ids)
            for name, item_id in self.ESSENTIAL_DUNGEON_LOOT.items()
        }
