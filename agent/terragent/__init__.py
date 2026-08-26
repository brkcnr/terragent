"""TerrAgent: Autonomous AI agent for Terraria.

This package provides the core client, reflex execution loop, combat engine,
arena builder, hellbridge builder, dungeon manager, hardmode manager,
housing manager, categorized storage, postmortem analysis, and schemas for
communicating with the TerrAgentBridge tModLoader mod.
"""

__version__ = "0.4.0"
__protocol_version__ = "1.0.0"

from terragent.arena import ArenaBuilder, ArenaSpec
from terragent.bridge_client import BridgeClient
from terragent.combat import CombatEngine, calculate_circle_kite_target, calculate_lead_aim
from terragent.config import BridgeConfig, ReflexConfig, TerrAgentConfig, load_config
from terragent.dungeon import DungeonManager
from terragent.hardmode import HardmodeManager, HardmodeStatus
from terragent.hellbridge import HellbridgeBuilder, HellbridgeSpec
from terragent.housing import (
    HousingManager,
    StructureTemplate,
    create_player_bedroom,
    create_standard_npc_room,
)
from terragent.memory import MemoryStore
from terragent.postmortem import PostmortemManager
from terragent.reflex import ReflexEngine
from terragent.schemas import (
    ActionResult,
    AttackCommand,
    BreakTileCommand,
    BuffState,
    BuildStructureCommand,
    ChestItemSlot,
    DepositChestCommand,
    GameState,
    HandshakeRequest,
    HandshakeResponse,
    InteractNPCCommand,
    InventorySlot,
    MoveCommand,
    NearbyEnemy,
    PlaceTileCommand,
    PlayerState,
    QueryChestRequest,
    QueryChestResponse,
    QueryHousingRequest,
    QueryHousingResponse,
    SetSpawnCommand,
    TownNPC,
    UseItemCommand,
    UsePotionCommand,
    WithdrawChestCommand,
)
from terragent.storage import ItemCategory, StorageManager, categorize_item

__all__ = [
    "ActionResult",
    "ArenaBuilder",
    "ArenaSpec",
    "AttackCommand",
    "BreakTileCommand",
    "BridgeClient",
    "BridgeConfig",
    "BuffState",
    "BuildStructureCommand",
    "ChestItemSlot",
    "CombatEngine",
    "DepositChestCommand",
    "DungeonManager",
    "GameState",
    "HandshakeRequest",
    "HandshakeResponse",
    "HardmodeManager",
    "HardmodeStatus",
    "HellbridgeBuilder",
    "HellbridgeSpec",
    "HousingManager",
    "InteractNPCCommand",
    "InventorySlot",
    "ItemCategory",
    "MemoryStore",
    "MoveCommand",
    "NearbyEnemy",
    "PlaceTileCommand",
    "PlayerState",
    "PostmortemManager",
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
    "UseItemCommand",
    "UsePotionCommand",
    "WithdrawChestCommand",
    "__protocol_version__",
    "__version__",
    "calculate_circle_kite_target",
    "calculate_lead_aim",
    "categorize_item",
    "create_player_bedroom",
    "create_standard_npc_room",
    "load_config",
]
