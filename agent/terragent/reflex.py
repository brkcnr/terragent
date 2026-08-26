"""Reflex layer for real-time deterministic game reactions (Milestone 1 Scope).

This module executes zero-latency rule-based responses to incoming GameState
frames without invoking any LLM or network planning layers.
"""

import logging

from terragent.config import ReflexConfig
from terragent.schemas import GameState, MoveCommand

logger = logging.getLogger(__name__)


class ReflexEngine:
    """Deterministic rule-based reflex engine for Milestone 1.

    Monitors player state at tick rate and generates immediate reactive
    action commands when emergency conditions (e.g., low HP) are detected.
    """

    def __init__(self, config: ReflexConfig | None = None) -> None:
        """Initialize the Reflex engine.

        Args:
            config: Optional ReflexConfig instance. Defaults to standard settings.
        """
        self.config = config or ReflexConfig()

    def process_tick(self, state: GameState) -> MoveCommand | None:
        """Process an incoming GameState frame and decide on an immediate reflex action.

        Args:
            state: The current GameState snapshot received from the bridge.

        Returns:
            MoveCommand if an immediate reaction is triggered, or None if idle.
        """
        player = state.player

        # M1 Rule: If health drops below threshold, trigger immediate tactical retreat
        if player.hp < self.config.low_hp_threshold:
            target_x = player.x + self.config.safe_retreat_offset_x
            target_y = player.y

            logger.info(
                f"Reflex Triggered: Low HP ({player.hp}/{player.max_hp}). "
                f"Retreating from ({player.x:.1f}, {player.y:.1f}) to "
                f"({target_x:.1f}, {target_y:.1f})"
            )

            return MoveCommand(
                action="move_to",
                target_x=target_x,
                target_y=target_y,
                duration_ms=300,
            )

        # Standard healthy state: no emergency reflex action required
        return None
