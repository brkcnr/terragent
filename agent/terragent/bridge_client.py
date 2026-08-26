"""WebSocket client for communicating with the TerrAgentBridge tModLoader mod.

This module manages the connection lifecycle, protocol version negotiation,
automatic reconnection with exponential backoff, and bidirectional message transmission.
"""

import asyncio
import json
import logging
import random
from collections.abc import AsyncIterator
from typing import Any

from websockets.asyncio.client import ClientConnection, connect
from websockets.protocol import State

from terragent.config import BridgeConfig
from terragent.schemas import (
    ActionResult,
    BridgeConnectionError,
    BridgeTimeoutError,
    GameState,
    HandshakeRequest,
    HandshakeResponse,
    MoveCommand,
    ProtocolVersionMismatchError,
)

logger = logging.getLogger(__name__)


class BridgeClient:
    """Manages asynchronous WebSocket communication with the Terraria bridge mod.

    Attributes:
        config: Bridge configuration settings.
        ws: Active WebSocket client connection or None if disconnected.
    """

    def __init__(self, config: BridgeConfig | None = None) -> None:
        """Initialize the BridgeClient.

        Args:
            config: Optional bridge configuration. Defaults to standard settings.
        """
        self.config = config or BridgeConfig()
        self.ws: ClientConnection | None = None
        self._is_closing: bool = False

    @property
    def is_connected(self) -> bool:
        """Return True if WebSocket connection is open and active."""
        return self.ws is not None and self.ws.state == State.OPEN

    async def connect(self) -> None:
        """Establish connection to the bridge and verify protocol handshake.

        Raises:
            ProtocolVersionMismatchError: If server and client versions differ.
            BridgeConnectionError: If connection cannot be established or handshake fails.
        """
        url = f"ws://{self.config.host}:{self.config.port}"
        logger.info(f"Connecting to TerrAgentBridge at {url}...")

        try:
            self.ws = await asyncio.wait_for(
                connect(url),
                timeout=self.config.timeout_seconds,
            )
            await self._perform_handshake()
            logger.info(
                "Connected to TerrAgentBridge successfully "
                f"(Protocol v{self.config.protocol_version})"
            )
        except ProtocolVersionMismatchError:
            await self.disconnect()
            raise
        except TimeoutError as exc:
            await self.disconnect()
            raise BridgeTimeoutError(f"Connection timeout to {url}") from exc
        except Exception as exc:
            await self.disconnect()
            raise BridgeConnectionError(f"Failed to connect to {url}: {exc}") from exc

    async def connect_with_retry(self) -> None:
        """Attempt connection with exponential backoff and jitter.

        Raises:
            ProtocolVersionMismatchError: If version mismatch is detected (never retried).
            BridgeConnectionError: If maximum reconnect attempts are exceeded.
        """
        delay = self.config.reconnect_initial_delay_seconds
        attempts = 0

        while attempts < self.config.max_reconnect_attempts and not self._is_closing:
            attempts += 1
            try:
                await self.connect()
                return
            except ProtocolVersionMismatchError:
                # Version mismatches are fatal configuration errors; do not retry
                raise
            except (BridgeConnectionError, BridgeTimeoutError) as exc:
                logger.warning(
                    f"Bridge connection attempt {attempts}/{self.config.max_reconnect_attempts} "
                    f"failed: {exc}. Retrying in {delay:.2f}s..."
                )
                if attempts >= self.config.max_reconnect_attempts:
                    raise BridgeConnectionError(
                        f"Could not connect to bridge after {attempts} attempts."
                    ) from exc

                # Add +/- 15% random jitter to backoff
                jitter = delay * random.uniform(-0.15, 0.15)
                await asyncio.sleep(max(0.1, delay + jitter))
                delay = min(
                    delay * self.config.reconnect_backoff_factor,
                    self.config.reconnect_max_delay_seconds,
                )

    async def _perform_handshake(self) -> None:
        """Exchange and validate protocol version handshake.

        Raises:
            BridgeConnectionError: If WebSocket is not connected or message is invalid.
            ProtocolVersionMismatchError: If protocol versions do not match.
        """
        if self.ws is None or self.ws.state != State.OPEN:
            raise BridgeConnectionError("Cannot perform handshake: WebSocket is not open")

        # 1. Send HandshakeRequest
        req = HandshakeRequest(protocol_version=self.config.protocol_version)
        await self.ws.send(req.model_dump_json())

        # 2. Receive HandshakeResponse
        raw_resp = await asyncio.wait_for(
            self.ws.recv(),
            timeout=self.config.timeout_seconds,
        )
        data = json.loads(raw_resp)
        resp = HandshakeResponse.model_validate(data)

        if resp.protocol_version != self.config.protocol_version:
            raise ProtocolVersionMismatchError(
                server_version=resp.protocol_version,
                client_version=self.config.protocol_version,
            )

        if resp.status != "ok":
            raise BridgeConnectionError(f"Handshake rejected by server: {resp.message}")

    async def receive_game_state(self) -> GameState:
        """Receive and validate a single GameState message from the bridge.

        Returns:
            GameState: Parsed and validated game state model.

        Raises:
            BridgeConnectionError: If disconnected or received invalid message.
            BridgeTimeoutError: If receive times out.
        """
        if self.ws is None or self.ws.state != State.OPEN:
            raise BridgeConnectionError("Cannot receive game state: WebSocket is not connected")

        try:
            raw_msg = await asyncio.wait_for(
                self.ws.recv(),
                timeout=self.config.timeout_seconds,
            )
            data: dict[str, Any] = json.loads(raw_msg)
            return GameState.model_validate(data)
        except TimeoutError as exc:
            raise BridgeTimeoutError("Timed out waiting for GameState frame") from exc
        except Exception as exc:
            raise BridgeConnectionError(f"Error receiving GameState: {exc}") from exc

    async def listen_states(self) -> AsyncIterator[GameState]:
        """Continuously stream GameState messages from the bridge.

        Yields:
            GameState: Validated game state snapshots pushed by the bridge.

        Raises:
            BridgeConnectionError: If stream encounters an unrecoverable connection failure.
        """
        while self.is_connected and not self._is_closing:
            try:
                state = await self.receive_game_state()
                yield state
            except (BridgeConnectionError, BridgeTimeoutError) as exc:
                if self._is_closing:
                    break
                logger.warning(f"Connection lost during state stream: {exc}")
                raise

    async def send_command(self, command: MoveCommand) -> ActionResult | None:
        """Send an action command to the bridge mod.

        Args:
            command: The MoveCommand instance to transmit.

        Returns:
            ActionResult if returned by server, or None.

        Raises:
            BridgeConnectionError: If sending fails or socket is closed.
        """
        if self.ws is None or self.ws.state != State.OPEN:
            raise BridgeConnectionError("Cannot send command: WebSocket is not connected")

        try:
            await self.ws.send(command.model_dump_json())
            return None
        except Exception as exc:
            raise BridgeConnectionError(
                f"Failed to send command {command.command_id}: {exc}"
            ) from exc

    async def disconnect(self) -> None:
        """Close active WebSocket connection cleanly."""
        self._is_closing = True
        if self.ws is not None and self.ws.state == State.OPEN:
            try:
                await self.ws.close()
            except Exception as exc:
                logger.debug(f"Exception during WebSocket close: {exc}")
        self.ws = None
        self._is_closing = False
