"""Housing templates and validation manager for TerrAgent (Milestone 2 Scope).

This module implements parameterized grid-relative building templates for NPC housing
and player bedrooms adhering to official Terraria housing validation rules.
"""

import logging
from dataclasses import dataclass
from enum import StrEnum

from terragent.memory import MemoryStore
from terragent.schemas import PlaceTileCommand

logger = logging.getLogger(__name__)


class TileCategory(StrEnum):
    """Categorization of tile elements in a structure template."""

    SOLID_BLOCK = "solid_block"
    BACKGROUND_WALL = "background_wall"
    DOOR = "door"
    LIGHT_SOURCE = "light_source"
    FLAT_SURFACE = "flat_surface"
    COMFORT_ITEM = "comfort_item"
    BED = "bed"


# Item IDs standard in Terraria 1.4.4+
ITEM_WOOD = 9  # Wood block (solid)
ITEM_WOOD_WALL = 93  # Wood wall (background)
ITEM_WOOD_DOOR = 25  # Wooden Door
ITEM_WOOD_CHAIR = 34  # Wooden Chair
ITEM_WOOD_TABLE = 36  # Wooden Table
ITEM_TORCH = 8  # Torch
ITEM_BED = 224  # Wooden Bed


@dataclass(frozen=True)
class TemplateTile:
    """Relative placement coordinate and item ID within a structure template."""

    rel_x: int
    rel_y: int
    item_id: int
    category: TileCategory


class StructureTemplate:
    """Represents a parameterized, grid-relative building blueprint."""

    def __init__(self, name: str, width: int, height: int, tiles: list[TemplateTile]) -> None:
        """Initialize structure template.

        Args:
            name: Template identifier.
            width: Total exterior width in tiles.
            height: Total exterior height in tiles.
            tiles: List of TemplateTile placements relative to (0, 0) top-left.
        """
        self.name = name
        self.width = width
        self.height = height
        self.tiles = tiles

    def instantiate(self, origin_x: int, origin_y: int) -> list[PlaceTileCommand]:
        """Convert the relative blueprint into absolute PlaceTile commands.

        Args:
            origin_x: Absolute world tile coordinate X for top-left anchor.
            origin_y: Absolute world tile coordinate Y for top-left anchor.

        Returns:
            list[PlaceTileCommand]: Sequence of tile placement commands.
        """
        commands: list[PlaceTileCommand] = []
        for t in self.tiles:
            commands.append(
                PlaceTileCommand(
                    tile_x=origin_x + t.rel_x,
                    tile_y=origin_y + t.rel_y,
                    item_id=t.item_id,
                )
            )
        return commands

    @property
    def interior_center(self) -> tuple[int, int]:
        """Return relative (dx, dy) center tile inside the room for query verification."""
        return (self.width // 2, self.height // 2)


def create_standard_npc_room(
    interior_width: int = 10,
    interior_height: int = 6,
) -> StructureTemplate:
    """Generate a standard NPC housing blueprint conforming to Terraria rules.

    Dimensions:
        Interior: interior_width x interior_height (default 10x6 = 60 interior tiles)
        Exterior: (interior_width + 2) x (interior_height + 2) (default 12x8 = 96 total tiles)

    Components:
        - Solid wood floor, ceiling, and outer boundary frame
        - Background wood walls filling all interior tiles
        - Wooden door on left frame
        - Wooden table (flat surface) and Wooden chair (comfort item) on floor
        - Torch (light source) on upper interior wall

    Args:
        interior_width: Number of interior floor tiles.
        interior_height: Number of interior vertical tiles.

    Returns:
        StructureTemplate: Ready-to-instantiate room blueprint.
    """
    ext_width = interior_width + 2
    ext_height = interior_height + 2
    tiles: list[TemplateTile] = []

    # 1. Outer Frame (Solid Blocks) - Top & Bottom
    for x in range(ext_width):
        tiles.append(
            TemplateTile(rel_x=x, rel_y=0, item_id=ITEM_WOOD, category=TileCategory.SOLID_BLOCK)
        )
        tiles.append(
            TemplateTile(
                rel_x=x, rel_y=ext_height - 1, item_id=ITEM_WOOD, category=TileCategory.SOLID_BLOCK
            )
        )

    # Outer Frame - Left & Right walls (leaving 3 tiles on left for door at bottom)
    for y in range(1, ext_height - 1):
        # Right wall: solid wood
        tiles.append(
            TemplateTile(
                rel_x=ext_width - 1,
                rel_y=y,
                item_id=ITEM_WOOD,
                category=TileCategory.SOLID_BLOCK,
            )
        )

        # Left wall: solid wood for top part, door opening for bottom 3 tiles
        if y < ext_height - 4:
            tiles.append(
                TemplateTile(
                    rel_x=0,
                    rel_y=y,
                    item_id=ITEM_WOOD,
                    category=TileCategory.SOLID_BLOCK,
                )
            )

    # Door on left side (height 3)
    tiles.append(
        TemplateTile(
            rel_x=0,
            rel_y=ext_height - 4,
            item_id=ITEM_WOOD_DOOR,
            category=TileCategory.DOOR,
        )
    )

    # 2. Interior Background Walls
    for y in range(1, ext_height - 1):
        for x in range(1, ext_width - 1):
            tiles.append(
                TemplateTile(
                    rel_x=x,
                    rel_y=y,
                    item_id=ITEM_WOOD_WALL,
                    category=TileCategory.BACKGROUND_WALL,
                )
            )

    # 3. Furniture & Essentials (Floor is at y = ext_height - 1)
    floor_y = ext_height - 2
    # Table placed at x = 3
    tiles.append(
        TemplateTile(
            rel_x=3,
            rel_y=floor_y,
            item_id=ITEM_WOOD_TABLE,
            category=TileCategory.FLAT_SURFACE,
        )
    )
    # Chair placed next to table at x = 5
    tiles.append(
        TemplateTile(
            rel_x=5,
            rel_y=floor_y,
            item_id=ITEM_WOOD_CHAIR,
            category=TileCategory.COMFORT_ITEM,
        )
    )
    # Torch on wall at (x=6, y=2)
    tiles.append(
        TemplateTile(
            rel_x=6,
            rel_y=2,
            item_id=ITEM_TORCH,
            category=TileCategory.LIGHT_SOURCE,
        )
    )

    return StructureTemplate(
        name=f"npc_room_{interior_width}x{interior_height}",
        width=ext_width,
        height=ext_height,
        tiles=tiles,
    )


def create_player_bedroom(
    interior_width: int = 10,
    interior_height: int = 6,
) -> StructureTemplate:
    """Generate a player bedroom blueprint with a Wooden Bed to set base spawn.

    Args:
        interior_width: Number of interior floor tiles.
        interior_height: Number of interior vertical tiles.

    Returns:
        StructureTemplate: Bedroom blueprint with placed bed.
    """
    ext_width = interior_width + 2
    ext_height = interior_height + 2
    tiles: list[TemplateTile] = []

    # Outer Frame
    for x in range(ext_width):
        tiles.append(
            TemplateTile(rel_x=x, rel_y=0, item_id=ITEM_WOOD, category=TileCategory.SOLID_BLOCK)
        )
        tiles.append(
            TemplateTile(
                rel_x=x, rel_y=ext_height - 1, item_id=ITEM_WOOD, category=TileCategory.SOLID_BLOCK
            )
        )

    for y in range(1, ext_height - 1):
        tiles.append(
            TemplateTile(
                rel_x=ext_width - 1,
                rel_y=y,
                item_id=ITEM_WOOD,
                category=TileCategory.SOLID_BLOCK,
            )
        )
        if y < ext_height - 4:
            tiles.append(
                TemplateTile(
                    rel_x=0,
                    rel_y=y,
                    item_id=ITEM_WOOD,
                    category=TileCategory.SOLID_BLOCK,
                )
            )

    tiles.append(
        TemplateTile(
            rel_x=0,
            rel_y=ext_height - 4,
            item_id=ITEM_WOOD_DOOR,
            category=TileCategory.DOOR,
        )
    )

    # Background Walls
    for y in range(1, ext_height - 1):
        for x in range(1, ext_width - 1):
            tiles.append(
                TemplateTile(
                    rel_x=x,
                    rel_y=y,
                    item_id=ITEM_WOOD_WALL,
                    category=TileCategory.BACKGROUND_WALL,
                )
            )

    # Bed placed on floor at x=3, floor_y
    floor_y = ext_height - 2
    tiles.append(TemplateTile(rel_x=3, rel_y=floor_y, item_id=ITEM_BED, category=TileCategory.BED))
    # Torch
    tiles.append(
        TemplateTile(
            rel_x=6,
            rel_y=2,
            item_id=ITEM_TORCH,
            category=TileCategory.LIGHT_SOURCE,
        )
    )

    return StructureTemplate(
        name=f"player_bedroom_{interior_width}x{interior_height}",
        width=ext_width,
        height=ext_height,
        tiles=tiles,
    )


class HousingManager:
    """Orchestrates room generation, housing query verification, and NPC assignments."""

    # Priority Town NPCs for Milestone 2
    PRIORITY_NPCS = [
        {"type": 17, "name": "Merchant", "condition": "50+ silver coins in inventory"},
        {"type": 18, "name": "Nurse", "condition": "HP > 100 and Merchant present"},
        {"type": 19, "name": "Demolitionist", "condition": "Explosives and Merchant present"},
        {"type": 22, "name": "Guide", "condition": "Initial world spawn"},
    ]

    def __init__(self, memory: MemoryStore) -> None:
        """Initialize HousingManager with persistent memory store.

        Args:
            memory: Active MemoryStore instance.
        """
        self.memory = memory
        self.default_template = create_standard_npc_room()
        self.bedroom_template = create_player_bedroom()

    def plan_next_room(
        self,
        base_origin_x: int,
        base_origin_y: int,
        room_index: int,
    ) -> tuple[int, int, StructureTemplate]:
        """Compute the grid origin and template for the next room in the base housing block.

        Rooms are stacked horizontally and vertically adjacent to each other.

        Args:
            base_origin_x: Anchor tile X coordinate for base foundation.
            base_origin_y: Anchor tile Y coordinate for base foundation.
            room_index: Sequential index of the room being planned (0 = bedroom).

        Returns:
            tuple[int, int, StructureTemplate]: (origin_x, origin_y, template)
        """
        # Place up to 3 rooms per row, then stack a new row above
        col = room_index % 3
        row = room_index // 3

        origin_x = base_origin_x + col * (self.default_template.width - 1)
        origin_y = base_origin_y - row * (self.default_template.height - 1)

        template = self.bedroom_template if room_index == 0 else self.default_template
        return origin_x, origin_y, template

    def register_built_room(
        self,
        name: str,
        origin_x: int,
        origin_y: int,
        template: StructureTemplate,
    ) -> int:
        """Record newly constructed room in persistent memory.

        Args:
            name: Label for the room.
            origin_x: Top-left tile X coordinate.
            origin_y: Top-left tile Y coordinate.
            template: The blueprint used for construction.

        Returns:
            int: Created room ID.
        """
        return self.memory.record_room(
            name=name,
            origin_x=origin_x,
            origin_y=origin_y,
            width=template.width,
            height=template.height,
            is_valid=False,
            assigned_npc=None,
        )

    def get_housing_check_coordinate(self, room_id: int) -> tuple[int, int]:
        """Return the interior coordinate to pass to the bridge query_housing endpoint.

        Args:
            room_id: Room database ID.

        Returns:
            tuple[int, int]: (check_x, check_y) interior tile coordinates.

        Raises:
            ValueError: If room ID is not found.
        """
        room = self.memory.get_room(room_id)
        if not room:
            raise ValueError(f"Room with id {room_id} not found in database")

        check_x = room["origin_x"] + room["width"] // 2
        check_y = room["origin_y"] + room["height"] // 2
        return (check_x, check_y)
