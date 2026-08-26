"""Postmortem logging and combat attempt analysis for TerrAgent (Milestone 3 Scope).

This module records boss encounter outcomes into SQLite persistent memory,
tracks attempt counts against circuit breaker limits, and diagnoses failure patterns.
"""

import json
import logging
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class PostmortemManager:
    """Manages recording, counting, and diagnostic analysis of boss combat attempts."""

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        """Initialize SQLite database schema for boss attempts.

        Args:
            db_path: Path to database or ':memory:'.
        """
        self.db_path = str(db_path)
        self._is_memory = self.db_path == ":memory:"
        self._memory_conn: sqlite3.Connection | None = None
        if self._is_memory:
            self._memory_conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._memory_conn.row_factory = sqlite3.Row
        self._init_db()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager yielding an active SQLite connection with row factory."""
        if self._is_memory and self._memory_conn is not None:
            try:
                yield self._memory_conn
                self._memory_conn.commit()
            except Exception:
                self._memory_conn.rollback()
                raise
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

    def _init_db(self) -> None:
        """Create boss_attempts table if not already present."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS boss_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    boss_name TEXT NOT NULL,
                    attempt_number INTEGER NOT NULL,
                    outcome TEXT NOT NULL,
                    duration_seconds REAL NOT NULL,
                    damage_dealt INTEGER NOT NULL,
                    cause_of_death TEXT,
                    gear_used TEXT,
                    strategy_notes TEXT,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def record_attempt(
        self,
        boss_name: str,
        outcome: str,
        duration_seconds: float,
        damage_dealt: int,
        cause_of_death: str | None = None,
        gear_used: dict[str, Any] | None = None,
        strategy_notes: str = "",
    ) -> int:
        """Record a completed or failed boss attempt in the database.

        Args:
            boss_name: Unique boss identifier (e.g. 'eye_of_cthulhu').
            outcome: Encounter result ('victory', 'defeat', 'timeout', 'aborted').
            duration_seconds: Total fight time in seconds.
            damage_dealt: Total damage inflicted on the boss.
            cause_of_death: Detailed reason if the player died.
            gear_used: Snapshot of weapons and armor equipped.
            strategy_notes: Diagnostic notes.

        Returns:
            int: The generated attempt ID.
        """
        gear_json = json.dumps(gear_used or {})
        now = datetime.now(UTC).isoformat()
        current_attempts = self.get_attempt_count(boss_name)
        attempt_number = current_attempts + 1

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO boss_attempts
                (boss_name, attempt_number, outcome, duration_seconds,
                 damage_dealt, cause_of_death, gear_used, strategy_notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    boss_name,
                    attempt_number,
                    outcome,
                    duration_seconds,
                    damage_dealt,
                    cause_of_death,
                    gear_json,
                    strategy_notes,
                    now,
                ),
            )
            if cursor.lastrowid is None:
                raise RuntimeError("Failed to retrieve attempt ID from database")
            logger.info(
                f"Recorded boss attempt #{attempt_number} for '{boss_name}': "
                f"outcome={outcome}, duration={duration_seconds:.1f}s"
            )
            return int(cursor.lastrowid)

    def get_attempt_count(self, boss_name: str) -> int:
        """Return the number of previous attempts made against this boss."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM boss_attempts WHERE LOWER(boss_name) = LOWER(?)",
                (boss_name,),
            )
            return int(cursor.fetchone()[0])

    def get_attempts(self, boss_name: str) -> list[dict[str, Any]]:
        """Retrieve all recorded attempts for a boss ordered chronologically."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM boss_attempts
                WHERE LOWER(boss_name) = LOWER(?)
                ORDER BY attempt_number ASC
                """,
                (boss_name,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def analyze_failures(
        self,
        boss_name: str,
        max_allowed_attempts: int = 3,
    ) -> dict[str, Any]:
        """Analyze past failed attempts and determine adjustments or circuit breaker status.

        Args:
            boss_name: Boss identifier.
            max_allowed_attempts: Threshold before requiring manual intervention.

        Returns:
            dict: Analysis report including recommendation and human review flag.
        """
        attempts = self.get_attempts(boss_name)
        count = len(attempts)

        if not attempts:
            return {
                "boss_name": boss_name,
                "attempt_count": 0,
                "requires_human_review": False,
                "recommendation": "Ready for initial attempt.",
            }

        last_attempt = attempts[-1]
        if last_attempt["outcome"] == "victory":
            return {
                "boss_name": boss_name,
                "attempt_count": count,
                "requires_human_review": False,
                "recommendation": "Boss already defeated.",
            }

        requires_review = count >= max_allowed_attempts
        causes = [a["cause_of_death"] for a in attempts if a["cause_of_death"]]

        recommendations: list[str] = []
        if any("charge" in str(c).lower() for c in causes):
            recommendations.append("Increase arena platform length and use Swiftness potion.")
        if any("servant" in str(c).lower() or "minion" in str(c).lower() for c in causes):
            recommendations.append("Prioritize clearing minions with piercing Jester's arrows.")
        if not recommendations:
            recommendations.append("Upgrade armor tier or craft additional buff potions.")

        return {
            "boss_name": boss_name,
            "attempt_count": count,
            "max_allowed_attempts": max_allowed_attempts,
            "requires_human_review": requires_review,
            "last_outcome": last_attempt["outcome"],
            "recommendation": " ".join(recommendations),
        }
