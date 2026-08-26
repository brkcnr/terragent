"""Pydantic schemas for the TerrAgent bridge protocol (Milestone 1 Scope).

This module defines strongly typed models for WebSocket communication between
the Python agent and the C# tModLoader bridge mod.
"""

import uuid
from typing import Literal

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
    """Represents a single slot in the player's inventory hotbar."""

    slot: int = Field(ge=0, le=4, description="Hotbar slot index (0-4 for M1)")
    item_id: int = Field(ge=0, description="Terraria item type ID (0 for empty)")
    name: str = Field(default="", description="Name of the item")
    stack: int = Field(ge=0, default=0, description="Stack count")


class PlayerState(BaseModel):
    """Represents the player character state in Milestone 1."""

    hp: int = Field(description="Current health points")
    max_hp: int = Field(ge=1, description="Maximum health points")
    x: float = Field(description="World X coordinate in pixels")
    y: float = Field(description="World Y coordinate in pixels")
    selected_slot: int = Field(ge=0, le=4, default=0, description="Currently selected hotbar slot")
    inventory: list[InventorySlot] = Field(
        default_factory=list,
        description="First 5 inventory slots for M1",
    )


class GameState(BaseModel):
    """Periodic game state frame pushed by the bridge mod at ~10 Hz."""

    type: Literal["game_state"] = "game_state"
    protocol_version: str = "1.0.0"
    timestamp: float = Field(description="Unix timestamp in seconds")
    player: PlayerState = Field(description="Player character snapshot")


class MoveCommand(BaseModel):
    """Command requesting player movement to target coordinates."""

    type: Literal["action"] = "action"
    command_id: str = Field(
        default_factory=lambda: f"cmd_{uuid.uuid4().hex[:12]}",
        description="Unique identifier for command tracking",
    )
    action: Literal["move_to"] = "move_to"
    target_x: float = Field(description="Target world coordinate X")
    target_y: float = Field(description="Target world coordinate Y")
    duration_ms: int = Field(
        default=200,
        ge=1,
        le=5000,
        description="Duration in milliseconds to apply movement input",
    )


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
