"""Integration tests with a fake WebSocket bridge server (Milestones 1 to 4).

Tests connection, protocol handshake, state parsing with enemies and buffs,
command dispatch (movement, attack, potions, tiles, NPC interactions, item usage),
housing queries, chest queries, and error handling without needing Terraria installed.
"""

import asyncio
import json
from typing import Any

import pytest
from terragent.bridge_client import BridgeClient
from terragent.config import BridgeConfig
from terragent.schemas import (
    AttackCommand,
    BridgeConnectionError,
    GameState,
    InteractNPCCommand,
    ProtocolVersionMismatchError,
    UseItemCommand,
    UsePotionCommand,
)
from websockets.asyncio.server import ServerConnection, serve
from websockets.exceptions import ConnectionClosed


class FakeBridgeServer:
    """Mock WebSocket bridge server for automated testing."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8766,
        protocol_version: str = "1.0.0",
        reject_handshake: bool = False,
    ) -> None:
        """Initialize the fake bridge server."""
        self.host = host
        self.port = port
        self.protocol_version = protocol_version
        self.reject_handshake = reject_handshake
        self.received_commands: list[dict[str, Any]] = []
        self.received_queries: list[dict[str, Any]] = []
        self.server: Any = None
        self._stop_event = asyncio.Event()

    async def start(self) -> None:
        """Start the fake WebSocket server."""
        self.server = await serve(self._handle_client, self.host, self.port)

    async def stop(self) -> None:
        """Stop the fake WebSocket server and close connections."""
        self._stop_event.set()
        if self.server is not None:
            self.server.close()
            await self.server.wait_closed()

    async def _handle_client(self, websocket: ServerConnection) -> None:
        """Handle incoming client connection, handshake, queries, and mock stream."""
        try:
            # 1. Receive HandshakeRequest
            raw_req = await websocket.recv()
            req_data = json.loads(raw_req)

            # 2. Send HandshakeResponse
            resp_status = "error" if self.reject_handshake else "ok"
            resp = {
                "type": "handshake_ack",
                "server_name": "FakeTerrAgentBridge",
                "protocol_version": self.protocol_version,
                "status": resp_status,
                "message": "Handshake response from fake bridge",
            }
            await websocket.send(json.dumps(resp))

            if self.protocol_version != req_data.get("protocol_version") or self.reject_handshake:
                await websocket.close()
                return

            # 3. Stream a canned GameState with NPCs, Boss, Buffs, and Hardmode flag
            sample_state = {
                "type": "game_state",
                "protocol_version": self.protocol_version,
                "timestamp": 1724678400.0,
                "player": {
                    "hp": 180,
                    "max_hp": 200,
                    "defense": 14,
                    "x": 2500.0,
                    "y": 1200.0,
                    "selected_slot": 0,
                    "inventory": [
                        {"slot": 0, "item_id": 99, "name": "Gold Bow", "stack": 1},
                        {"slot": 1, "item_id": 3507, "name": "Copper Shortsword", "stack": 1},
                    ],
                    "buffs": [
                        {"buff_id": 5, "name": "Ironskin", "duration_seconds": 240.0},
                    ],
                },
                "town_npcs": [
                    {"npc_type": 22, "name": "Andrew", "is_housed": True, "room_id": 1},
                    {"npc_type": 17, "name": "Alfred", "is_housed": True, "room_id": 2},
                ],
                "nearby_enemies": [
                    {
                        "enemy_id": 4,
                        "name": "Eye of Cthulhu",
                        "hp": 2800,
                        "max_hp": 2800,
                        "x": 2700.0,
                        "y": 1100.0,
                        "velocity_x": -3.0,
                        "velocity_y": 1.0,
                        "distance": 223.6,
                        "is_boss": True,
                    }
                ],
                "spawn_tile_x": 125,
                "spawn_tile_y": 80,
                "is_hardmode": True,
                "time_of_day": 12000.0,
                "is_night": False,
            }
            await websocket.send(json.dumps(sample_state))

            # Listen for incoming client commands and queries
            async for raw_msg in websocket:
                msg_data = json.loads(raw_msg)
                msg_type = msg_data.get("type", "")

                if msg_type == "query":
                    self.received_queries.append(msg_data)
                    q_name = msg_data.get("query", "")
                    q_id = msg_data.get("query_id", "")

                    if q_name == "query_housing":
                        housing_resp = {
                            "type": "query_response",
                            "query_id": q_id,
                            "query": "query_housing",
                            "success": True,
                            "is_valid": True,
                            "failure_reason": None,
                            "assigned_npc": "Merchant",
                            "details": "Room valid",
                        }
                        await websocket.send(json.dumps(housing_resp))

                    elif q_name == "query_chest":
                        chest_resp = {
                            "type": "query_response",
                            "query_id": q_id,
                            "query": "query_chest",
                            "success": True,
                            "chest_x": msg_data.get("chest_x", 0),
                            "chest_y": msg_data.get("chest_y", 0),
                            "items": [
                                {"slot": 0, "item_id": 12, "name": "Iron Ore", "stack": 75},
                            ],
                            "details": "Chest items queried",
                        }
                        await websocket.send(json.dumps(chest_resp))

                elif msg_type == "action":
                    self.received_commands.append(msg_data)

        except ConnectionClosed:
            pass


@pytest.mark.asyncio
async def test_bridge_connection_and_combat_dispatch() -> None:
    """Test connection, GameState parsing with Hardmode flag, and command dispatch."""
    server = FakeBridgeServer(port=8766)
    await server.start()

    config = BridgeConfig(host="127.0.0.1", port=8766, protocol_version="1.0.0")
    client = BridgeClient(config)

    try:
        await client.connect()
        assert client.is_connected

        # Receive game state and verify Hardmode & Enemies
        state = await client.receive_game_state()
        assert isinstance(state, GameState)
        assert state.is_hardmode is True
        assert len(state.nearby_enemies) == 1
        assert state.nearby_enemies[0].name == "Eye of Cthulhu"

        # Dispatch Combat, NPC Interaction, and Item Usage Actions
        await client.send_command(AttackCommand(aim_x=2700.0, aim_y=1100.0, use_item_slot=0))
        await client.send_command(UsePotionCommand(potion_type="healing"))
        await client.send_command(InteractNPCCommand(npc_name="Old Man", option_index=0))
        await client.send_command(UseItemCommand(slot=0, target_x=2500.0, target_y=1200.0))

        await asyncio.sleep(0.05)
        assert len(server.received_commands) == 4
        assert server.received_commands[0]["action"] == "attack"
        assert server.received_commands[1]["action"] == "use_potion"
        assert server.received_commands[2]["action"] == "interact_npc"
        assert server.received_commands[3]["action"] == "use_item"

    finally:
        await client.disconnect()
        await server.stop()


@pytest.mark.asyncio
async def test_bridge_protocol_version_mismatch() -> None:
    """Test that protocol version mismatch raises ProtocolVersionMismatchError."""
    server = FakeBridgeServer(port=8767, protocol_version="2.0.0")
    await server.start()

    # Client expects v1.0.0, server provides v2.0.0
    config = BridgeConfig(host="127.0.0.1", port=8767, protocol_version="1.0.0")
    client = BridgeClient(config)

    try:
        with pytest.raises(ProtocolVersionMismatchError) as exc_info:
            await client.connect()

        assert exc_info.value.server_version == "2.0.0"
        assert exc_info.value.client_version == "1.0.0"
        assert not client.is_connected
    finally:
        await client.disconnect()
        await server.stop()


@pytest.mark.asyncio
async def test_bridge_handshake_rejection() -> None:
    """Test server handshake rejection."""
    server = FakeBridgeServer(port=8768, reject_handshake=True)
    await server.start()

    config = BridgeConfig(host="127.0.0.1", port=8768, protocol_version="1.0.0")
    client = BridgeClient(config)

    try:
        with pytest.raises(BridgeConnectionError, match="Handshake rejected"):
            await client.connect()
    finally:
        await client.disconnect()
        await server.stop()


@pytest.mark.asyncio
async def test_bridge_connection_refused() -> None:
    """Test client reaction when bridge server is not running."""
    config = BridgeConfig(host="127.0.0.1", port=8799, timeout_seconds=1.0)
    client = BridgeClient(config)

    with pytest.raises(BridgeConnectionError):
        await client.connect()

    assert not client.is_connected
