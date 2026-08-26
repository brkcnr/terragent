"""Underworld Hellbridge construction manager for TerrAgent (Milestone 4 Scope).

This module constructs extensive horizontal platform runways across Underworld lava lakes,
clears obsidian ruin obstructions, and places life-regeneration stations for the
Wall of Flesh encounter.
"""

import logging
from dataclasses import dataclass

from terragent.arena import ITEM_CAMPFIRE, ITEM_HEART_LANTERN, ITEM_WOOD_PLATFORM
from terragent.schemas import BreakTileCommand, PlaceTileCommand

logger = logging.getLogger(__name__)


@dataclass
class HellbridgeSpec:
    """Configuration parameters defining Hellbridge dimensions and buff placement."""

    start_x: int = 1500
    end_x: int = 3000
    bridge_y: int = 3200
    clear_height: int = 4
    campfire_spacing: int = 60
    heart_lantern_spacing: int = 60


class HellbridgeBuilder:
    """Generates tile placement and demolition commands for the Underworld runway."""

    def __init__(self, spec: HellbridgeSpec | None = None) -> None:
        """Initialize HellbridgeBuilder with layout specifications.

        Args:
            spec: Optional custom HellbridgeSpec. Defaults to standard 1500-tile bridge.
        """
        self.spec = spec or HellbridgeSpec()

    def generate_hellbridge_commands(
        self,
        known_obstacle_tiles: list[tuple[int, int]] | None = None,
    ) -> list[PlaceTileCommand | BreakTileCommand]:
        """Generate sequence of commands to lay runway and clear vertical obstructions.

        Args:
            known_obstacle_tiles: Optional list of ruin/obsidian tile coordinates to breach.

        Returns:
            list[PlaceTileCommand | BreakTileCommand]: Ordered construction/demolition actions.
        """
        commands: list[PlaceTileCommand | BreakTileCommand] = []

        # 1. Break recorded obstacles intersecting the running path (head clearance)
        if known_obstacle_tiles:
            for ox, oy in known_obstacle_tiles:
                if (
                    self.spec.start_x <= ox <= self.spec.end_x
                    and self.spec.bridge_y - self.spec.clear_height <= oy < self.spec.bridge_y
                ):
                    commands.append(BreakTileCommand(tile_x=ox, tile_y=oy))

        # 2. Lay continuous wooden platform runway across the Underworld
        for x in range(self.spec.start_x, self.spec.end_x):
            commands.append(
                PlaceTileCommand(
                    tile_x=x,
                    tile_y=self.spec.bridge_y,
                    item_id=ITEM_WOOD_PLATFORM,
                )
            )

        # 3. Place Campfires at regular intervals along the runway
        for x in range(self.spec.start_x + 20, self.spec.end_x - 20, self.spec.campfire_spacing):
            commands.append(
                PlaceTileCommand(
                    tile_x=x,
                    tile_y=self.spec.bridge_y - 1,
                    item_id=ITEM_CAMPFIRE,
                )
            )

        # 4. Place Heart Lanterns hanging below platform where feasible
        lantern_range = range(
            self.spec.start_x + 40,
            self.spec.end_x - 40,
            self.spec.heart_lantern_spacing,
        )
        for x in lantern_range:
            commands.append(
                PlaceTileCommand(
                    tile_x=x,
                    tile_y=self.spec.bridge_y + 1,
                    item_id=ITEM_HEART_LANTERN,
                )
            )

        total_length = self.spec.end_x - self.spec.start_x
        logger.info(
            f"Generated Hellbridge commands: length={total_length} tiles, "
            f"bridge_y={self.spec.bridge_y}, total_actions={len(commands)}"
        )
        return commands
