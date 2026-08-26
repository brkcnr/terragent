"""Integration tests with a fake WebSocket bridge server (Milestone 1).

Tests connection, protocol handshake, state parsing, command dispatch,
and error/mismatch handling without needing Terraria installed.
"""

import asyncio
import json
from typing import Any

import pytest
from terragent.bridge_client import BridgeClient
from terragent.config import BridgeConfig
from terragent.schemas import (
    BridgeConnectionError,
    GameState,
    MoveCommand,
    ProtocolVersionMismatchError,
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
        """Handle incoming client connection, handshake, and mock stream."""
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

            # 3. Stream a canned GameState and listen for commands
            sample_state = {
                "type": "game_state",
                "protocol_version": self.protocol_version,
                "timestamp": 1724678400.0,
                "player": {
                    "hp": 90,
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
            await websocket.send(json.dumps(sample_state))

            # Listen for incoming client commands
            async for raw_msg in websocket:
                msg_data = json.loads(raw_msg)
                self.received_commands.append(msg_data)

        except ConnectionClosed:
            pass


@pytest.mark.asyncio
async def test_bridge_connection_success() -> None:
    """Test successful connection, handshake, and GameState reception."""
    server = FakeBridgeServer(port=8766)
    await server.start()

    config = BridgeConfig(host="127.0.0.1", port=8766, protocol_version="1.0.0")
    client = BridgeClient(config)

    try:
        await client.connect()
        assert client.is_connected

        # Receive game state
        state = await client.receive_game_state()
        assert isinstance(state, GameState)
        assert state.player.hp == 90
        assert state.player.x == 2500.0
        assert state.player.inventory[0].name == "Copper Shortsword"

        # Send MoveTo command
        cmd = MoveCommand(target_x=2600.0, target_y=1200.0, duration_ms=400)
        await client.send_command(cmd)

        # Give server a moment to receive
        await asyncio.sleep(0.05)
        assert len(server.received_commands) == 1
        assert server.received_commands[0]["action"] == "move_to"
        assert server.received_commands[0]["target_x"] == 2600.0

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
