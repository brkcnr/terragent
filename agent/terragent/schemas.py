"""Pydantic schemas for the TerrAgent bridge protocol (Milestones 1, 2 & 3).

This module defines strongly typed models for WebSocket communication between
the Python agent and the C# tModLoader bridge mod, covering player state,
enemies, buffs, combat actions, potion consumption, and queries.
"""

import uuid
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class ProtocolVersionMismatchError(Exception):
    """Raised when the server and client protocol versions do not match."""

    def __init__(self, server_version: str, client_version: str) -> None:
        """Initialize the exception with version details.

        Args:
            server_version: The protocol version reported by the server.
            client_version: The protocol version expected by the client.
        """
        super().__init__(
            f"Protocol version mismatch: server reported '{server_version}', "
            f"client expects '{client_version}'. Both must match exactly."
        )
        self.server_version = server_version
        self.client_version = client_version


class BridgeConnectionError(Exception):
    """Raised when communication with the bridge fails or is terminated."""


class BridgeTimeoutError(BridgeConnectionError):
    """Raised when an operation times out while waiting for the bridge."""


class HandshakeRequest(BaseModel):
    """Handshake request sent by the client upon establishing a connection."""

    type: Literal["handshake"] = "handshake"
    client_name: str = "TerrAgent-Python"
    protocol_version: str = "1.0.0"


class HandshakeResponse(BaseModel):
    """Handshake acknowledgement sent by the bridge mod."""

    type: Literal["handshake_ack"] = "handshake_ack"
    server_name: str = "TerrAgentBridge-tModLoader"
    protocol_version: str = "1.0.0"
    status: Literal["ok", "error"] = "ok"
    message: str = "Connected successfully"


class InventorySlot(BaseModel):
    """Represents a single slot in the player's inventory."""

    slot: int = Field(ge=0, le=58, description="Inventory slot index (0-4 hotbar, 0-49 main)")
    item_id: int = Field(ge=0, description="Terraria item type ID (0 for empty)")
    name: str = Field(default="", description="Name of the item")
    stack: int = Field(ge=0, default=0, description="Stack count")


class BuffState(BaseModel):
    """Represents an active buff or debuff affecting the player."""

    buff_id: int = Field(description="Terraria internal buff type ID")
    name: str = Field(description="Display name of the buff (e.g. 'Ironskin')")
    duration_seconds: float = Field(ge=0.0, description="Remaining duration in seconds")


class NearbyEnemy(BaseModel):
    """Represents a hostile NPC or boss within scanner radius."""

    enemy_id: int = Field(description="Terraria NPC slot index / ID")
    name: str = Field(description="Enemy name")
    hp: int = Field(description="Current enemy health")
    max_hp: int = Field(ge=1, description="Max enemy health")
    x: float = Field(description="World position X in pixels")
    y: float = Field(description="World position Y in pixels")
    velocity_x: float = Field(default=0.0, description="Movement velocity X")
    velocity_y: float = Field(default=0.0, description="Movement velocity Y")
    distance: float = Field(default=0.0, ge=0.0, description="Distance from player in pixels")
    is_boss: bool = Field(default=False, description="Whether this entity is a boss")


class TownNPC(BaseModel):
    """Represents a Town NPC status in the roster."""

    npc_type: int = Field(description="NPC type identifier (e.g. 17 Merchant, 18 Nurse)")
    name: str = Field(description="Individual NPC name")
    is_housed: bool = Field(default=False, description="Assigned to valid housing")
    room_id: int | None = Field(default=None, description="Assigned room identifier")


class PlayerState(BaseModel):
    """Represents the player character state."""

    hp: int = Field(description="Current health points")
    max_hp: int = Field(ge=1, description="Maximum health points")
    defense: int = Field(default=0, ge=0, description="Player defense rating")
    x: float = Field(description="World X coordinate in pixels")
    y: float = Field(description="World Y coordinate in pixels")
    selected_slot: int = Field(ge=0, le=49, default=0, description="Selected hotbar slot")
    inventory: list[InventorySlot] = Field(
        default_factory=list,
        description="Player inventory slots",
    )
    buffs: list[BuffState] = Field(
        default_factory=list,
        description="Active player buffs",
    )


class GameState(BaseModel):
    """Periodic game state frame pushed by the bridge mod at ~10 Hz."""

    type: Literal["game_state"] = "game_state"
    protocol_version: str = "1.0.0"
    timestamp: float = Field(description="Unix timestamp in seconds")
    player: PlayerState = Field(description="Player character snapshot")
    town_npcs: list[TownNPC] = Field(
        default_factory=list,
        description="Town NPC roster status",
    )
    nearby_enemies: list[NearbyEnemy] = Field(
        default_factory=list,
        description="Hostile entities currently detected around player",
    )
    spawn_tile_x: int | None = Field(default=None, description="Bed spawn tile X if set")
    spawn_tile_y: int | None = Field(default=None, description="Bed spawn tile Y if set")


# ==========================================
# Action Commands
# ==========================================


class BaseActionCommand(BaseModel):
    """Base class for all client-to-server action commands."""

    type: Literal["action"] = "action"
    command_id: str = Field(
        default_factory=lambda: f"cmd_{uuid.uuid4().hex[:12]}",
        description="Unique identifier for command tracking",
    )


class MoveCommand(BaseActionCommand):
    """Command requesting player movement to target coordinates."""

    action: Literal["move_to"] = "move_to"
    target_x: float = Field(description="Target world coordinate X")
    target_y: float = Field(description="Target world coordinate Y")
    duration_ms: int = Field(
        default=200,
        ge=1,
        le=5000,
        description="Duration in milliseconds to apply movement input",
    )


class AttackCommand(BaseActionCommand):
    """Command requesting weapon usage directed at specific aim coordinates."""

    action: Literal["attack"] = "attack"
    aim_x: float = Field(description="Target aim coordinate X in world space")
    aim_y: float = Field(description="Target aim coordinate Y in world space")
    use_item_slot: int = Field(default=0, ge=0, le=49, description="Inventory hotbar slot to use")
    continuous: bool = Field(default=True, description="Whether to sustain continuous attack input")


class UsePotionCommand(BaseActionCommand):
    """Command requesting potion consumption (healing, mana, or buff)."""

    action: Literal["use_potion"] = "use_potion"
    potion_type: Literal["healing", "mana", "buff"] = Field(
        default="healing",
        description="Type of potion to consume",
    )


class PlaceTileCommand(BaseActionCommand):
    """Command requesting tile or furniture placement at world grid coordinates."""

    action: Literal["place_tile"] = "place_tile"
    tile_x: int = Field(description="Tile grid coordinate X")
    tile_y: int = Field(description="Tile grid coordinate Y")
    item_id: int = Field(description="Item ID to place (block, wall, furniture, or torch)")


class BreakTileCommand(BaseActionCommand):
    """Command requesting tile or obstacle removal at world grid coordinates."""

    action: Literal["break_tile"] = "break_tile"
    tile_x: int = Field(description="Tile grid coordinate X")
    tile_y: int = Field(description="Tile grid coordinate Y")


class SetSpawnCommand(BaseActionCommand):
    """Command requesting bed interaction to set the player's spawn point."""

    action: Literal["set_spawn"] = "set_spawn"
    tile_x: int = Field(description="Bed head/foot tile grid coordinate X")
    tile_y: int = Field(description="Bed head/foot tile grid coordinate Y")


class DepositChestCommand(BaseActionCommand):
    """Command requesting deposit of an item stack into a specific chest."""

    action: Literal["deposit_chest"] = "deposit_chest"
    chest_x: int = Field(description="Chest tile grid coordinate X")
    chest_y: int = Field(description="Chest tile grid coordinate Y")
    inventory_slot: int = Field(ge=0, le=49, description="Source inventory slot")
    target_chest_slot: int | None = Field(
        default=None,
        description="Optional target chest slot index (0-39)",
    )


class WithdrawChestCommand(BaseActionCommand):
    """Command requesting withdrawal of an item stack from a chest into inventory."""

    action: Literal["withdraw_chest"] = "withdraw_chest"
    chest_x: int = Field(description="Chest tile grid coordinate X")
    chest_y: int = Field(description="Chest tile grid coordinate Y")
    chest_slot: int = Field(ge=0, le=39, description="Source chest slot index")
    target_inventory_slot: int | None = Field(
        default=None,
        description="Optional target inventory slot",
    )


class BuildStructureCommand(BaseActionCommand):
    """Command requesting programmatic construction of a template structure."""

    action: Literal["build_structure"] = "build_structure"
    template_name: str = Field(description="Structure template identifier")
    origin_x: int = Field(description="Anchor origin tile coordinate X")
    origin_y: int = Field(description="Anchor origin tile coordinate Y")


ActionCommand = Annotated[
    MoveCommand
    | AttackCommand
    | UsePotionCommand
    | PlaceTileCommand
    | BreakTileCommand
    | SetSpawnCommand
    | DepositChestCommand
    | WithdrawChestCommand
    | BuildStructureCommand,
    Field(discriminator="action"),
]


class ActionResult(BaseModel):
    """Result report returned after executing an action command."""

    type: Literal["action_result"] = "action_result"
    command_id: str = Field(description="ID of the command this result corresponds to")
    action: str = Field(description="Action name that was executed")
    success: bool = Field(description="Whether the action succeeded")
    execution_time_ms: float = Field(ge=0.0, description="Time taken to execute the action in ms")
    failure_reason: str | None = Field(
        default=None,
        description="Typed failure code if execution failed",
    )
    details: str = Field(default="", description="Human-readable result summary")


# ==========================================
# Bridge Queries (Request-Response)
# ==========================================


class BaseQueryRequest(BaseModel):
    """Base class for client-initiated queries."""

    type: Literal["query"] = "query"
    query_id: str = Field(
        default_factory=lambda: f"qry_{uuid.uuid4().hex[:12]}",
        description="Unique identifier for query tracking",
    )


class QueryHousingRequest(BaseQueryRequest):
    """Query checking in-game housing validity at a specific tile."""

    query: Literal["query_housing"] = "query_housing"
    tile_x: int = Field(description="Interior tile coordinate X")
    tile_y: int = Field(description="Interior tile coordinate Y")


class QueryHousingResponse(BaseModel):
    """Response returned for housing validity query."""

    type: Literal["query_response"] = "query_response"
    query_id: str = Field(description="Matching query ID")
    query: Literal["query_housing"] = "query_housing"
    success: bool = Field(description="Whether query was executed successfully")
    is_valid: bool = Field(description="Whether the room constitutes valid NPC housing")
    failure_reason: str | None = Field(
        default=None,
        description="Reason for invalidity if is_valid is False",
    )
    assigned_npc: str | None = Field(
        default=None,
        description="Name of NPC currently assigned to this room, if any",
    )
    details: str = Field(default="", description="Human-readable query summary")


class ChestItemSlot(BaseModel):
    """Represents an item occupying a chest slot."""

    slot: int = Field(ge=0, le=39, description="Chest slot index (0-39)")
    item_id: int = Field(ge=0, description="Item type ID")
    name: str = Field(default="", description="Item name")
    stack: int = Field(ge=0, description="Item stack count")


class QueryChestRequest(BaseQueryRequest):
    """Query requesting the item contents of a chest at specific tile coordinates."""

    query: Literal["query_chest"] = "query_chest"
    chest_x: int = Field(description="Chest tile coordinate X")
    chest_y: int = Field(description="Chest tile coordinate Y")


class QueryChestResponse(BaseModel):
    """Response containing chest contents."""

    type: Literal["query_response"] = "query_response"
    query_id: str = Field(description="Matching query ID")
    query: Literal["query_chest"] = "query_chest"
    success: bool = Field(description="Whether chest query succeeded")
    chest_x: int = Field(description="Chest tile coordinate X")
    chest_y: int = Field(description="Chest tile coordinate Y")
    items: list[ChestItemSlot] = Field(default_factory=list, description="Items present in chest")
    details: str = Field(default="", description="Query details")
