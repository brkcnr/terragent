"""Endgame progression, Celestial Pillars, Moon Lord, and run reporting for TerrAgent (M6 Scope).

This module coordinates Plantera, Golem, Lunatic Cultist, Celestial Pillars shield tracking,
Moon Lord encounter management, and generates the final end-to-end run report.
"""

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

CANONICAL_PILLARS = {"solar", "vortex", "nebula", "stardust"}
PILLAR_SHIELD_QUOTA = 100


@dataclass
class EndgameStatus:
    """Snapshot representing the endgame progression state."""

    plantera_defeated: bool = False
    golem_defeated: bool = False
    cultist_defeated: bool = False
    pillars_cleared: set[str] = field(default_factory=set)
    moon_lord_defeated: bool = False


class EndgameManager:
    """Manages endgame boss progression, pillar shield mechanics, and final run reporting."""

    def __init__(self) -> None:
        """Initialize EndgameManager with zero progression."""
        self.status = EndgameStatus()
        self.pillar_kill_counts: dict[str, int] = dict.fromkeys(CANONICAL_PILLARS, 0)

    def record_pillar_enemy_kill(self, pillar_name: str, count: int = 1) -> bool:
        """Record enemy defeat in proximity to a Celestial Pillar.

        Args:
            pillar_name: One of 'solar', 'vortex', 'nebula', 'stardust'.
            count: Number of enemies defeated.

        Returns:
            bool: True if shield quota is fulfilled (shield drops).
        """
        norm_name = pillar_name.lower()
        if norm_name in self.pillar_kill_counts:
            self.pillar_kill_counts[norm_name] += count
            current = self.pillar_kill_counts[norm_name]
            logger.info(f"Pillar [{norm_name}] kills: {current}/{PILLAR_SHIELD_QUOTA}")
            return current >= PILLAR_SHIELD_QUOTA
        return False

    def mark_pillar_destroyed(self, pillar_name: str) -> None:
        """Mark a Celestial Pillar as destroyed."""
        norm_name = pillar_name.lower()
        self.status.pillars_cleared.add(norm_name)
        cleared_count = len(self.status.pillars_cleared)
        logger.info(f"Celestial Pillar [{norm_name}] destroyed! Cleared: {cleared_count}/4")

    def are_all_pillars_cleared(self) -> bool:
        """Return True if all 4 Celestial Pillars have been destroyed."""
        return CANONICAL_PILLARS.issubset(self.status.pillars_cleared)

    def evaluate_moon_lord_readiness(
        self,
        player_defense: int,
        has_wings: bool,
        ammo_count: int,
        min_defense: int = 70,
        min_ammo: int = 1500,
    ) -> tuple[bool, str]:
        """Verify gear, wing status, and ammo reserves before summoning Moon Lord.

        Args:
            player_defense: Total player defense.
            has_wings: Whether wings are equipped.
            ammo_count: Available Chlorophyte/Crystal ammo count.
            min_defense: Defense threshold.
            min_ammo: Minimum ammo threshold.

        Returns:
            tuple[bool, str]: (is_ready, rationale_message)
        """
        if not has_wings:
            return False, "Wings required for laser dodging during Moon Lord encounter."
        if player_defense < min_defense:
            return (
                False,
                f"Player defense ({player_defense}) is below minimum requirement ({min_defense}).",
            )
        if ammo_count < min_ammo:
            return False, f"Ammo count ({ammo_count}) is below minimum reserve ({min_ammo})."

        return True, "Ready for Moon Lord confrontation."

    def generate_final_run_report(
        self,
        total_playtime_seconds: float,
        housed_npcs_count: int,
        categorized_chests_count: int,
        attempt_history: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Compile a comprehensive JSON run report summarizing the full autonomous playthrough.

        Args:
            total_playtime_seconds: Elapsed in-game runtime in seconds.
            housed_npcs_count: Total Town NPCs safely housed.
            categorized_chests_count: Total categorized chests configured.
            attempt_history: Full history of boss attempts from PostmortemManager.

        Returns:
            dict[str, Any]: Structured run report.
        """
        hours = int(total_playtime_seconds // 3600)
        minutes = int((total_playtime_seconds % 3600) // 60)
        seconds = int(total_playtime_seconds % 60)
        formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        victories = [a["boss_name"] for a in attempt_history if a.get("outcome") == "victory"]
        defeats = [a for a in attempt_history if a.get("outcome") == "defeat"]

        outcome_status = (
            "VICTORY: Moon Lord Defeated — Full Game Autonomous Clear"
            if self.status.moon_lord_defeated
            else "IN_PROGRESS: Endgame progression active"
        )

        report = {
            "run_status": outcome_status,
            "total_playtime": formatted_time,
            "playtime_seconds": total_playtime_seconds,
            "progression_milestones": {
                "m1_bootstrap": True,
                "m2_base_and_npcs": housed_npcs_count >= 3,
                "m3_pre_hardmode_combat": "eye_of_cthulhu" in victories,
                "m4_hardmode_transition": "wall_of_flesh" in victories,
                "m5_mechanical_bosses": (
                    "the_destroyer" in victories
                    and "the_twins" in victories
                    and "skeletron_prime" in victories
                ),
                "m6_endgame_moon_lord": self.status.moon_lord_defeated,
            },
            "world_statistics": {
                "town_npcs_housed": housed_npcs_count,
                "categorized_chests": categorized_chests_count,
                "celestial_pillars_destroyed": len(self.status.pillars_cleared),
            },
            "boss_combat_metrics": {
                "total_attempts": len(attempt_history),
                "total_victories": len(victories),
                "total_defeats": len(defeats),
                "unique_bosses_defeated": list(set(victories)),
            },
        }

        logger.info(f"Generated run report: status='{outcome_status}', playtime={formatted_time}")
        return report
