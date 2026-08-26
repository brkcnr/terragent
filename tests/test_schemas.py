"""Unit tests for TerrAgent Milestone 1 schemas."""

import json

import pytest
from pydantic import ValidationError
from terragent.schemas import (
    ActionResult,
    GameState,
    HandshakeRequest,
    HandshakeResponse,
    InventorySlot,
    MoveCommand,
    ProtocolVersionMismatchError,
)


def test_handshake_request_defaults() -> None:
    """Test HandshakeRequest default serialization."""
    req = HandshakeRequest()
    assert req.type == "handshake"
    assert req.client_name == "TerrAgent-Python"
    assert req.protocol_version == "1.0.0"

    data = json.loads(req.model_dump_json())
    assert data["type"] == "handshake"
    assert data["protocol_version"] == "1.0.0"


def test_handshake_response_validation() -> None:
    """Test HandshakeResponse parsing."""
    raw = {
        "type": "handshake_ack",
        "server_name": "TerrAgentBridge-tModLoader",
        "protocol_version": "1.0.0",
        "status": "ok",
        "message": "Connected",
    }
    resp = HandshakeResponse.model_validate(raw)
    assert resp.status == "ok"
    assert resp.protocol_version == "1.0.0"


def test_inventory_slot_bounds() -> None:
    """Test InventorySlot validation constraints."""
    slot = InventorySlot(slot=0, item_id=3507, name="Copper Shortsword", stack=1)
    assert slot.slot == 0
    assert slot.item_id == 3507
    assert slot.stack == 1

    # M1 slot out of bounds (> 4)
    with pytest.raises(ValidationError):
        InventorySlot(slot=5, item_id=1, name="Dirt", stack=1)

    # Negative slot
    with pytest.raises(ValidationError):
        InventorySlot(slot=-1, item_id=1, name="Dirt", stack=1)


def test_game_state_parsing() -> None:
    """Test complete GameState parsing and serialization."""
    raw = {
        "type": "game_state",
        "protocol_version": "1.0.0",
        "timestamp": 1724678400.0,
        "player": {
            "hp": 100,
            "max_hp": 100,
            "x": 2500.0,
            "y": 1200.0,
            "selected_slot": 0,
            "inventory": [
                {"slot": 0, "item_id": 3507, "name": "Copper Shortsword", "stack": 1},
                {"slot": 1, "item_id": 3509, "name": "Copper Pickaxe", "stack": 1},
            ],
        },
    }
    state = GameState.model_validate(raw)
    assert state.player.hp == 100
    assert state.player.x == 2500.0
    assert len(state.player.inventory) == 2
    assert state.player.inventory[0].name == "Copper Shortsword"


def test_move_command_creation() -> None:
    """Test MoveCommand defaults and validation."""
    cmd = MoveCommand(target_x=2550.0, target_y=1200.0)
    assert cmd.action == "move_to"
    assert cmd.target_x == 2550.0
    assert cmd.target_y == 1200.0
    assert cmd.duration_ms == 200
    assert cmd.command_id.startswith("cmd_")


def test_action_result_parsing() -> None:
    """Test ActionResult model parsing."""
    raw = {
        "type": "action_result",
        "command_id": "cmd_123",
        "action": "move_to",
        "success": True,
        "execution_time_ms": 195.5,
        "failure_reason": None,
        "details": "Success",
    }
    result = ActionResult.model_validate(raw)
    assert result.success is True
    assert result.execution_time_ms == 195.5
    assert result.failure_reason is None


def test_protocol_version_mismatch_exception() -> None:
    """Test ProtocolVersionMismatchError message formatting."""
    exc = ProtocolVersionMismatchError("1.1.0", "1.0.0")
    assert "server reported '1.1.0'" in str(exc)
    assert "client expects '1.0.0'" in str(exc)
    assert exc.server_version == "1.1.0"
    assert exc.client_version == "1.0.0"
