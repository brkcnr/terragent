"""Persistent memory and SQLite storage for TerrAgent (Milestone 2 Scope).

This module manages relational persistence for NPC housing rooms, town NPC roster,
categorized chests, and item inventory indexing.
"""

import logging
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from terragent.schemas import ChestItemSlot, TownNPC

logger = logging.getLogger(__name__)


class MemoryStore:
    """Manages SQLite storage for world state, rooms, NPCs, and categorized chests.

    Attributes:
        db_path: Path to the SQLite database file or ':memory:' for tests.
    """

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        """Initialize the database and ensure required tables exist.

        Args:
            db_path: Filepath to SQLite database or ':memory:'.
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
        """Initialize relational database tables and indices."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 1. Rooms table (NPC Housing)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rooms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    origin_x INTEGER NOT NULL,
                    origin_y INTEGER NOT NULL,
                    width INTEGER NOT NULL,
                    height INTEGER NOT NULL,
                    is_valid BOOLEAN NOT NULL DEFAULT 0,
                    assigned_npc TEXT,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 2. Town NPCs roster table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS town_npcs (
                    npc_type INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    is_housed BOOLEAN NOT NULL DEFAULT 0,
                    room_id INTEGER,
                    last_seen TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (room_id) REFERENCES rooms (id)
                )
            """)

            # 3. Categorized chests table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tile_x INTEGER NOT NULL,
                    tile_y INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    label TEXT NOT NULL,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(tile_x, tile_y)
                )
            """)

            # 4. Chest items index table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chest_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chest_id INTEGER NOT NULL,
                    slot INTEGER NOT NULL,
                    item_id INTEGER NOT NULL,
                    item_name TEXT NOT NULL,
                    stack INTEGER NOT NULL,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (chest_id) REFERENCES chests (id) ON DELETE CASCADE,
                    UNIQUE(chest_id, slot)
                )
            """)

            # 5. Base spawn point
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS base_spawn (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    tile_x INTEGER NOT NULL,
                    tile_y INTEGER NOT NULL,
                    is_set BOOLEAN NOT NULL DEFAULT 1,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

    # ==========================================
    # Housing & Room Methods
    # ==========================================

    def record_room(
        self,
        name: str,
        origin_x: int,
        origin_y: int,
        width: int,
        height: int,
        is_valid: bool = False,
        assigned_npc: str | None = None,
    ) -> int:
        """Insert or record a built room in the database.

        Args:
            name: Descriptive room identifier.
            origin_x: Top-left tile coordinate X.
            origin_y: Top-left tile coordinate Y.
            width: Exterior room width in tiles.
            height: Exterior room height in tiles.
            is_valid: Whether confirmed valid by housing query.
            assigned_npc: Name of assigned Town NPC.

        Returns:
            int: The generated room ID.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO rooms
                (name, origin_x, origin_y, width, height, is_valid, assigned_npc)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (name, origin_x, origin_y, width, height, int(is_valid), assigned_npc),
            )
            if cursor.lastrowid is None:
                raise RuntimeError("Failed to retrieve generated room ID from database insert")
            return int(cursor.lastrowid)

    def update_room_validity(
        self,
        room_id: int,
        is_valid: bool,
        assigned_npc: str | None = None,
    ) -> None:
        """Update housing validity and assigned NPC for an existing room.

        Args:
            room_id: Unique room ID.
            is_valid: New validity state.
            assigned_npc: Optional assigned NPC name.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE rooms
                SET is_valid = ?, assigned_npc = ?
                WHERE id = ?
                """,
                (int(is_valid), assigned_npc, room_id),
            )

    def get_room(self, room_id: int) -> dict[str, Any] | None:
        """Fetch a specific room by its ID.

        Args:
            room_id: Database room identifier.

        Returns:
            dict or None: Room fields if found.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM rooms WHERE id = ?", (room_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_valid_rooms(self) -> list[dict[str, Any]]:
        """Return all rooms confirmed valid for NPC housing.

        Returns:
            list[dict]: List of valid room records.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM rooms WHERE is_valid = 1")
            return [dict(row) for row in cursor.fetchall()]

    def get_unassigned_rooms(self) -> list[dict[str, Any]]:
        """Return all valid rooms that do not yet have an assigned NPC.

        Returns:
            list[dict]: Unoccupied valid room records.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM rooms "
                "WHERE is_valid = 1 AND (assigned_npc IS NULL OR assigned_npc = '')"
            )
            return [dict(row) for row in cursor.fetchall()]

    # ==========================================
    # NPC Roster Methods
    # ==========================================

    def sync_npc_roster(self, town_npcs: list[TownNPC]) -> None:
        """Synchronize the live Town NPC roster with persistent memory.

        Args:
            town_npcs: Current TownNPC snapshot list from GameState.
        """
        now = datetime.now(UTC).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for npc in town_npcs:
                cursor.execute(
                    """
                    INSERT INTO town_npcs (npc_type, name, is_housed, room_id, last_seen)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(npc_type) DO UPDATE SET
                        name = excluded.name,
                        is_housed = excluded.is_housed,
                        room_id = excluded.room_id,
                        last_seen = excluded.last_seen
                    """,
                    (npc.npc_type, npc.name, int(npc.is_housed), npc.room_id, now),
                )

    def get_housed_npcs(self) -> list[dict[str, Any]]:
        """Retrieve all currently housed Town NPCs.

        Returns:
            list[dict]: Housed Town NPC records.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM town_npcs WHERE is_housed = 1")
            return [dict(row) for row in cursor.fetchall()]

    def count_housed_npcs(self) -> int:
        """Count the number of confirmed housed Town NPCs.

        Returns:
            int: Number of housed NPCs.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM town_npcs WHERE is_housed = 1")
            return int(cursor.fetchone()[0])

    # ==========================================
    # Categorized Chests & Storage Index
    # ==========================================

    def register_chest(
        self,
        tile_x: int,
        tile_y: int,
        category: str,
        label: str = "",
    ) -> int:
        """Register or update a chest location and its assigned item category.

        Args:
            tile_x: Tile grid coordinate X.
            tile_y: Tile grid coordinate Y.
            category: Storage category string.
            label: Optional human-readable label.

        Returns:
            int: The chest ID.
        """
        now = datetime.now(UTC).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO chests (tile_x, tile_y, category, label, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(tile_x, tile_y) DO UPDATE SET
                    category = excluded.category,
                    label = excluded.label,
                    updated_at = excluded.updated_at
                """,
                (tile_x, tile_y, category, label or category, now),
            )
            cursor.execute(
                "SELECT id FROM chests WHERE tile_x = ? AND tile_y = ?",
                (tile_x, tile_y),
            )
            return int(cursor.fetchone()[0])

    def update_chest_contents(
        self,
        tile_x: int,
        tile_y: int,
        items: list[ChestItemSlot],
    ) -> None:
        """Replace all stored item entries for a specific chest with fresh scan data.

        Args:
            tile_x: Tile coordinate X.
            tile_y: Tile coordinate Y.
            items: Scanned item slots in this chest.

        Raises:
            ValueError: If no chest exists at coordinates.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM chests WHERE tile_x = ? AND tile_y = ?",
                (tile_x, tile_y),
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"No chest registered at coordinates ({tile_x}, {tile_y})")

            chest_id = int(row[0])
            now = datetime.now(UTC).isoformat()

            # Delete old items in this chest
            cursor.execute("DELETE FROM chest_items WHERE chest_id = ?", (chest_id,))

            # Insert current item slots (skipping empty 0-stack items)
            for it in items:
                if it.stack > 0 and it.item_id > 0:
                    cursor.execute(
                        """
                        INSERT INTO chest_items
                        (chest_id, slot, item_id, item_name, stack, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (chest_id, it.slot, it.item_id, it.name, it.stack, now),
                    )

    def get_chest_by_location(self, tile_x: int, tile_y: int) -> dict[str, Any] | None:
        """Fetch chest information and contents by tile coordinates.

        Args:
            tile_x: Chest tile X.
            tile_y: Chest tile Y.

        Returns:
            dict or None: Chest metadata and items array.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chests WHERE tile_x = ? AND tile_y = ?", (tile_x, tile_y))
            row = cursor.fetchone()
            if not row:
                return None

            chest_data = dict(row)
            cursor.execute(
                "SELECT * FROM chest_items WHERE chest_id = ? ORDER BY slot ASC",
                (chest_data["id"],),
            )
            chest_data["items"] = [dict(it) for it in cursor.fetchall()]
            return chest_data

    def get_chests_by_category(self, category: str) -> list[dict[str, Any]]:
        """Retrieve all chests assigned to a specific category.

        Args:
            category: Storage category name.

        Returns:
            list[dict]: Matching chest records.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chests WHERE category = ?", (category,))
            return [dict(row) for row in cursor.fetchall()]

    def find_item_in_chests(self, item_name_or_id: str | int) -> list[dict[str, Any]]:
        """Find which chests contain an item by name or item ID.

        Args:
            item_name_or_id: Target item ID or name string.

        Returns:
            list[dict]: Item rows with chest location details.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if isinstance(item_name_or_id, int):
                cursor.execute(
                    """
                    SELECT c.id as chest_id, c.tile_x, c.tile_y, c.category,
                           ci.slot, ci.item_id, ci.item_name, ci.stack
                    FROM chest_items ci
                    JOIN chests c ON c.id = ci.chest_id
                    WHERE ci.item_id = ?
                    """,
                    (item_name_or_id,),
                )
            else:
                cursor.execute(
                    """
                    SELECT c.id as chest_id, c.tile_x, c.tile_y, c.category,
                           ci.slot, ci.item_id, ci.item_name, ci.stack
                    FROM chest_items ci
                    JOIN chests c ON c.id = ci.chest_id
                    WHERE LOWER(ci.item_name) = LOWER(?)
                    """,
                    (item_name_or_id,),
                )
            return [dict(row) for row in cursor.fetchall()]

    # ==========================================
    # Base Spawn Point
    # ==========================================

    def set_spawn_point(self, tile_x: int, tile_y: int) -> None:
        """Record the player's base bed spawn point.

        Args:
            tile_x: Spawn tile coordinate X.
            tile_y: Spawn tile coordinate Y.
        """
        now = datetime.now(UTC).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO base_spawn (id, tile_x, tile_y, is_set, updated_at)
                VALUES (1, ?, ?, 1, ?)
                ON CONFLICT(id) DO UPDATE SET
                    tile_x = excluded.tile_x,
                    tile_y = excluded.tile_y,
                    is_set = 1,
                    updated_at = excluded.updated_at
                """,
                (tile_x, tile_y, now),
            )

    def get_spawn_point(self) -> tuple[int, int] | None:
        """Get the current base bed spawn point coordinates if set.

        Returns:
            tuple[int, int] or None: (tile_x, tile_y) coordinates.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT tile_x, tile_y FROM base_spawn WHERE id = 1 AND is_set = 1")
            row = cursor.fetchone()
            if row:
                return (int(row[0]), int(row[1]))
            return None
