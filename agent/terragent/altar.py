"""Hardmode Altar smashing and ore tier progression manager for TerrAgent (Milestone 5 Scope).

This module coordinates Demon/Crimson Altar breaking using the Pwnhammer,
tracking unlocked Hardmode ore tiers (Cobalt/Palladium, Mythril/Orichalcum, Adamantite/Titanium).
"""

import logging
from enum import StrEnum

from terragent.schemas import BreakTileCommand

logger = logging.getLogger(__name__)


class HardmodeOreTier(StrEnum):
    """Hardmode ore tier hierarchy unlocked by smashing altars."""

    TIER_1_COBALT_PALLADIUM = "cobalt_or_palladium"
    TIER_2_MYTHRIL_ORICHALCUM = "mythril_or_orichalcum"
    TIER_3_ADAMANTITE_TITANIUM = "adamantite_or_titanium"


class AltarManager:
    """Manages altar demolition targets and maps altars smashed to ore tiers."""

    def __init__(self, altars_broken: int = 0) -> None:
        """Initialize AltarManager with count of broken altars."""
        self.altars_broken = altars_broken

    def get_unlocked_tiers(self) -> list[HardmodeOreTier]:
        """Return the list of hardmode ore tiers spawned in the world.

        Returns:
            list[HardmodeOreTier]: Active ore tiers present.
        """
        tiers: list[HardmodeOreTier] = []
        if self.altars_broken >= 1:
            tiers.append(HardmodeOreTier.TIER_1_COBALT_PALLADIUM)
        if self.altars_broken >= 2:
            tiers.append(HardmodeOreTier.TIER_2_MYTHRIL_ORICHALCUM)
        if self.altars_broken >= 3:
            tiers.append(HardmodeOreTier.TIER_3_ADAMANTITE_TITANIUM)
        return tiers

    def plan_altar_breaking(
        self,
        known_altar_coords: list[tuple[int, int]],
        target_total_altars: int = 6,
    ) -> list[BreakTileCommand]:
        """Generate BreakTileCommands to reach target broken altar quota.

        Args:
            known_altar_coords: List of discovered (tile_x, tile_y) coordinates.
            target_total_altars: Desired total altars to break (standard: 6).

        Returns:
            list[BreakTileCommand]: Actions to break necessary altars.
        """
        needed = max(0, target_total_altars - self.altars_broken)
        targets_to_break = known_altar_coords[:needed]

        commands: list[BreakTileCommand] = []
        for x, y in targets_to_break:
            commands.append(BreakTileCommand(tile_x=x, tile_y=y))

        logger.info(
            f"Planned breaking {len(commands)} altars to reach quota {target_total_altars} "
            f"(currently broken: {self.altars_broken})"
        )
        return commands

    def record_altar_broken(self, count: int = 1) -> None:
        """Increment count of smashed altars."""
        self.altars_broken += count
        logger.info(f"Altars broken updated to {self.altars_broken}")
