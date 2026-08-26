"""Arena generation and construction manager for TerrAgent (Milestone 3 Scope).

This module constructs multi-tiered wooden platform arenas complete with
buff stations (Campfires, Heart Lanterns, Sunflowers) optimized for boss encounters.
"""

import logging
from dataclasses import dataclass

from terragent.schemas import PlaceTileCommand

logger = logging.getLogger(__name__)

# Item IDs for arena construction
ITEM_WOOD_PLATFORM = 94  # Wooden Platform
ITEM_CAMPFIRE = 96  # Campfire (+0.5 HP/s life regen)
ITEM_HEART_LANTERN = 1290  # Heart Lantern (+1.0 HP/s life regen)
ITEM_SUNFLOWER = 63  # Sunflower (+10% move speed, Happy! buff)


@dataclass
class ArenaSpec:
    """Configuration parameters defining arena layout and dimensions."""

    layers: int = 3
    platform_length: int = 100
    layer_spacing: int = 6
    campfire_spacing: int = 40
    heart_lantern_spacing: int = 40
    sunflower_spacing: int = 50


class ArenaBuilder:
    """Generates deterministic tile placement commands for multi-tiered boss arenas."""

    def __init__(self, spec: ArenaSpec | None = None) -> None:
        """Initialize ArenaBuilder with layout specifications.

        Args:
            spec: Optional custom ArenaSpec. Defaults to standard 3-tier layout.
        """
        self.spec = spec or ArenaSpec()

    def generate_arena_commands(
        self,
        origin_x: int,
        origin_y: int,
    ) -> list[PlaceTileCommand]:
        """Generate sequence of PlaceTileCommands to construct the complete arena.

        Platforms are built centered on origin_x, stacking upward from origin_y.

        Args:
            origin_x: Horizontal center tile coordinate for the arena.
            origin_y: Base ground tile coordinate Y.

        Returns:
            list[PlaceTileCommand]: Ordered list of placement commands.
        """
        commands: list[PlaceTileCommand] = []
        half_length = self.spec.platform_length // 2
        start_x = origin_x - half_length
        end_x = origin_x + half_length

        for layer in range(self.spec.layers):
            # Platform layers stack upward from base (decreasing Y in Terraria coordinates)
            platform_y = origin_y - (layer + 1) * self.spec.layer_spacing

            # 1. Place horizontal wooden platform row
            for x in range(start_x, end_x):
                commands.append(
                    PlaceTileCommand(
                        tile_x=x,
                        tile_y=platform_y,
                        item_id=ITEM_WOOD_PLATFORM,
                    )
                )

            # 2. Place Campfires at regular intervals along this tier
            for x in range(start_x + 10, end_x - 10, self.spec.campfire_spacing):
                commands.append(
                    PlaceTileCommand(
                        tile_x=x,
                        tile_y=platform_y - 1,  # Sits on top of platform
                        item_id=ITEM_CAMPFIRE,
                    )
                )

            # 3. Place Heart Lanterns hanging beneath platform tiers (except lowest ground)
            if layer > 0:
                for x in range(start_x + 20, end_x - 20, self.spec.heart_lantern_spacing):
                    commands.append(
                        PlaceTileCommand(
                            tile_x=x,
                            tile_y=platform_y + 1,  # Hangs below platform
                            item_id=ITEM_HEART_LANTERN,
                        )
                    )

        # 4. Place Sunflowers on the base ground layer for movement speed bonus
        for x in range(start_x + 5, end_x - 5, self.spec.sunflower_spacing):
            commands.append(
                PlaceTileCommand(
                    tile_x=x,
                    tile_y=origin_y - 1,
                    item_id=ITEM_SUNFLOWER,
                )
            )

        logger.info(
            f"Generated {len(commands)} arena commands across {self.spec.layers} layers "
            f"spanning X=[{start_x}, {end_x}]"
        )
        return commands

    def get_arena_bounds(
        self,
        origin_x: int,
        origin_y: int,
    ) -> tuple[int, int, int, int]:
        """Compute the bounding box of the generated arena in tile coordinates.

        Args:
            origin_x: Arena center X.
            origin_y: Arena base Y.

        Returns:
            tuple[int, int, int, int]: (min_x, min_y, max_x, max_y)
        """
        half_length = self.spec.platform_length // 2
        min_x = origin_x - half_length
        max_x = origin_x + half_length
        min_y = origin_y - self.spec.layers * self.spec.layer_spacing
        max_y = origin_y
        return (min_x, min_y, max_x, max_y)
