"""Hardmode state transition and safety protocol manager for TerrAgent (Milestone 4 Scope).

This module coordinates post-Wall of Flesh world state transitions, verifies
Pwnhammer acquisition, and initiates base quarantine protocols.
"""

import logging
from dataclasses import dataclass

from terragent.schemas import GameState

logger = logging.getLogger(__name__)

ITEM_PWNHAMMER = 367  # Guaranteed drop from Wall of Flesh


@dataclass
class HardmodeStatus:
    """Snapshot representing the Hardmode transition progression."""

    is_hardmode: bool
    has_pwnhammer: bool
    safety_quarantine_active: bool
    transition_ready_for_m5: bool
    status_summary: str


class HardmodeManager:
    """Manages world state transition from Pre-Hardmode to Hardmode."""

    def __init__(self) -> None:
        """Initialize HardmodeManager."""
        self._hardmode_confirmed: bool = False
        self._pwnhammer_confirmed: bool = False

    def evaluate_transition(
        self,
        game_state: GameState,
        owned_item_ids: set[int],
    ) -> HardmodeStatus:
        """Evaluate whether Hardmode has been entered and next steps are unlocked.

        Args:
            game_state: Current GameState snapshot.
            owned_item_ids: Set of item IDs present in inventory and chests.

        Returns:
            HardmodeStatus: Current transition analysis.
        """
        is_hm = game_state.is_hardmode
        has_hammer = ITEM_PWNHAMMER in owned_item_ids

        if not is_hm:
            return HardmodeStatus(
                is_hardmode=False,
                has_pwnhammer=False,
                safety_quarantine_active=False,
                transition_ready_for_m5=False,
                status_summary="World is currently in Pre-Hardmode.",
            )

        if not self._hardmode_confirmed:
            logger.info("HARDMODE TRANSITION DETECTED! Initiating post-WoF safety protocol.")
            self._hardmode_confirmed = True

        if has_hammer:
            self._pwnhammer_confirmed = True

        # In Hardmode, activate base quarantine until player is geared for hardmode ores
        quarantine = is_hm and not has_hammer
        ready_for_m5 = is_hm and has_hammer

        summary = (
            "Hardmode Active! Pwnhammer secured. Ready for Altar Smash and Hardmode Ore Tiers (M5)."
            if ready_for_m5
            else "Hardmode Active! Retrieve Pwnhammer from Underworld WoF drop."
        )

        return HardmodeStatus(
            is_hardmode=is_hm,
            has_pwnhammer=has_hammer,
            safety_quarantine_active=quarantine,
            transition_ready_for_m5=ready_for_m5,
            status_summary=summary,
        )
