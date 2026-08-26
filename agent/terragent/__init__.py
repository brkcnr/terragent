"""TerrAgent: Autonomous AI agent for Terraria.

This package provides the core client, reflex execution loop, housing manager,
categorized storage, persistent SQLite memory, and schemas for communicating
with the TerrAgentBridge tModLoader mod.
"""

__version__ = "0.2.0"
__protocol_version__ = "1.0.0"

from terragent.bridge_client import BridgeClient
from terragent.config import BridgeConfig, ReflexConfig, TerrAgentConfig, load_config
from terragent.housing import (
    HousingManager,
    StructureTemplate,
    create_player_bedroom,
    create_standard_npc_room,
)
from terragent.memory import MemoryStore
from terragent.reflex import ReflexEngine
from terragent.schemas import (
    ActionResult,
    BreakTileCommand,
    BuildStructureCommand,
    ChestItemSlot,
    DepositChestCommand,
    GameState,
    HandshakeRequest,
    HandshakeResponse,
    InventorySlot,
    MoveCommand,
    PlaceTileCommand,
    PlayerState,
    QueryChestRequest,
    QueryChestResponse,
    QueryHousingRequest,
    QueryHousingResponse,
    SetSpawnCommand,
    TownNPC,
    WithdrawChestCommand,
)
from terragent.storage import ItemCategory, StorageManager, categorize_item

__all__ = [
    "ActionResult",
    "BreakTileCommand",
    "BridgeClient",
    "BridgeConfig",
    "BuildStructureCommand",
    "ChestItemSlot",
    "DepositChestCommand",
    "GameState",
    "HandshakeRequest",
    "HandshakeResponse",
    "HousingManager",
    "InventorySlot",
    "ItemCategory",
    "MemoryStore",
    "MoveCommand",
    "PlaceTileCommand",
    "PlayerState",
    "QueryChestRequest",
    "QueryChestResponse",
    "QueryHousingRequest",
    "QueryHousingResponse",
    "ReflexConfig",
    "ReflexEngine",
    "SetSpawnCommand",
    "StorageManager",
    "StructureTemplate",
    "TerrAgentConfig",
    "TownNPC",
    "WithdrawChestCommand",
    "__protocol_version__",
    "__version__",
    "categorize_item",
    "create_player_bedroom",
    "create_standard_npc_room",
    "load_config",
]
