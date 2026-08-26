"""Main entrypoint for running the TerrAgent autonomous agent.

Provides CLI argument parsing, lifecycle management, and the core event
dispatch loop for Milestone 1.
"""

import argparse
import asyncio
import logging
import signal
import sys

from terragent.bridge_client import BridgeClient
from terragent.config import TerrAgentConfig, load_config
from terragent.reflex import ReflexEngine
from terragent.schemas import BridgeConnectionError, ProtocolVersionMismatchError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("terragent")


async def run_agent(config: TerrAgentConfig) -> None:
    """Run the TerrAgent main reflex loop.

    Args:
        config: The loaded TerrAgent configuration.
    """
    logger.info("Initializing TerrAgent (Milestone 1 Bootstrap)...")
    client = BridgeClient(config=config.bridge)
    reflex = ReflexEngine(config=config.reflex)

    stop_event = asyncio.Event()

    def handle_signal() -> None:
        """Signal handler for graceful shutdown."""
        logger.info("Termination signal received. Shutting down gracefully...")
        stop_event.set()

    # Register OS signals where available (Unix / Windows compatibility)
    loop = asyncio.get_running_loop()
    try:
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, handle_signal)
    except NotImplementedError:
        # Windows loop might not support add_signal_handler for all signals
        pass

    try:
        await client.connect_with_retry()

        async for state in client.listen_states():
            if stop_event.is_set():
                break

            action = reflex.process_tick(state)
            if action is not None:
                await client.send_command(action)

    except ProtocolVersionMismatchError as exc:
        logger.error(f"Fatal protocol error: {exc}")
    except BridgeConnectionError as exc:
        logger.error(f"Bridge connection terminated: {exc}")
    except asyncio.CancelledError:
        logger.info("Agent execution task was cancelled.")
    finally:
        logger.info("Disconnecting from bridge...")
        await client.disconnect()
        logger.info("TerrAgent stopped cleanly.")


def cli_entrypoint() -> None:
    """CLI entrypoint invoked when running python -m terragent or terragent command."""
    parser = argparse.ArgumentParser(
        description="TerrAgent: Autonomous Terraria agent (Milestone 1)"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="configs/default.yaml",
        help="Path to YAML configuration file",
    )
    args = parser.parse_args()

    try:
        config = load_config(args.config)
    except Exception as exc:
        logger.error(f"Failed to load configuration: {exc}")
        sys.exit(1)

    try:
        asyncio.run(run_agent(config))
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received. Exiting.")
        sys.exit(0)


if __name__ == "__main__":
    cli_entrypoint()
