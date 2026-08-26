"""TerrAgent: Autonomous AI agent for Terraria.

This package provides the core client, reflex execution loop, and
schemas for communicating with the TerrAgentBridge tModLoader mod.
"""

__version__ = "0.1.0"
__protocol_version__ = "1.0.0"

from terragent.config import BridgeConfig, ReflexConfig, TerrAgentConfig, load_config
from terragent.schemas import (
    ActionResult,
    GameState,
    HandshakeRequest,
    HandshakeResponse,
    InventorySlot,
    MoveCommand,
    PlayerState,
)

__all__ = [
    "ActionResult",
    "BridgeConfig",
    "GameState",
    "HandshakeRequest",
    "HandshakeResponse",
    "InventorySlot",
    "MoveCommand",
    "PlayerState",
    "ReflexConfig",
    "TerrAgentConfig",
    "__protocol_version__",
    "__version__",
    "load_config",
]
