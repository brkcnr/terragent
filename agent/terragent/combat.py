"""Reflex combat engine and kiting controllers for TerrAgent (Milestone 3 Scope).

This module implements deterministic, zero-latency combat reactions including
vector-based circle kiting, horizontal platform sprinting, lead aiming, weapon selection,
and automatic potion healing.
"""

import math
from dataclasses import dataclass
from typing import Any

from terragent.schemas import (
    ActionCommand,
    AttackCommand,
    GameState,
    MoveCommand,
    NearbyEnemy,
    UsePotionCommand,
)


@dataclass
class CombatState:
    """Maintains transient combat tracking state across reflex ticks."""

    moving_right: bool = True
    last_heal_tick: float = 0.0
    last_buff_tick: float = 0.0
    orbit_angle_rad: float = 0.0


def calculate_lead_aim(
    player_x: float,
    player_y: float,
    target_x: float,
    target_y: float,
    target_vx: float = 0.0,
    target_vy: float = 0.0,
    projectile_speed: float = 14.0,
) -> tuple[float, float]:
    """Calculate predicted aim coordinates factoring in target velocity.

    Args:
        player_x: Player X coordinate.
        player_y: Player Y coordinate.
        target_x: Current target entity X coordinate.
        target_y: Current target entity Y coordinate.
        target_vx: Target horizontal velocity.
        target_vy: Target vertical velocity.
        projectile_speed: Arrow/projectile velocity in pixels per frame.

    Returns:
        tuple[float, float]: Predicted aim coordinates (aim_x, aim_y).
    """
    dx = target_x - player_x
    dy = target_y - player_y
    distance = math.hypot(dx, dy)

    if projectile_speed <= 0.0 or distance <= 0.0:
        return target_x, target_y

    time_to_target = distance / projectile_speed
    predicted_x = target_x + target_vx * time_to_target
    predicted_y = target_y + target_vy * time_to_target

    return predicted_x, predicted_y


def calculate_circle_kite_target(
    player_x: float,
    player_y: float,
    boss_x: float,
    boss_y: float,
    ideal_distance: float = 250.0,
    clockwise: bool = True,
    step_angle_rad: float = 0.3,
) -> tuple[float, float]:
    """Compute orbital reposition target around boss to maintain safe distance.

    Args:
        player_x: Player position X.
        player_y: Player position Y.
        boss_x: Boss position X.
        boss_y: Boss position Y.
        ideal_distance: Desired orbital radius in pixels.
        clockwise: Direction of orbit.
        step_angle_rad: Angular movement increment per step.

    Returns:
        tuple[float, float]: Desired world coordinates (target_x, target_y).
    """
    current_angle = math.atan2(player_y - boss_y, player_x - boss_x)
    direction = 1.0 if clockwise else -1.0
    next_angle = current_angle + direction * step_angle_rad

    target_x = boss_x + ideal_distance * math.cos(next_angle)
    target_y = boss_y + ideal_distance * math.sin(next_angle)

    return target_x, target_y


def calculate_horizontal_run_target(
    player_x: float,
    player_y: float,
    arena_min_x: float,
    arena_max_x: float,
    moving_right: bool,
    margin_px: float = 100.0,
    sprint_distance: float = 300.0,
) -> tuple[float, float, bool]:
    """Compute linear sprint target along arena platforms with border turnaround.

    Args:
        player_x: Player position X.
        player_y: Player position Y.
        arena_min_x: Left boundary of the arena in world coordinates.
        arena_max_x: Right boundary of the arena in world coordinates.
        moving_right: Current horizontal heading.
        margin_px: Distance from border triggering turnaround.
        sprint_distance: Step distance to run per movement command.

    Returns:
        tuple[float, float, bool]: (target_x, target_y, updated_moving_right)
    """
    # Turn around if approaching arena edges
    if moving_right and player_x >= arena_max_x - margin_px:
        moving_right = False
    elif not moving_right and player_x <= arena_min_x + margin_px:
        moving_right = True

    step = sprint_distance if moving_right else -sprint_distance
    target_x = player_x + step
    target_x = max(arena_min_x, min(arena_max_x, target_x))

    return target_x, player_y, moving_right


class CombatEngine:
    """Executes high-frequency reflex combat decisions, aim, and kiting."""

    def __init__(self) -> None:
        """Initialize CombatEngine with clean state tracking."""
        self.state = CombatState()

    def select_priority_target(
        self,
        enemies: list[NearbyEnemy],
        priority_rule: str = "servants_then_boss",
    ) -> NearbyEnemy | None:
        """Identify the highest threat enemy entity to engage.

        Args:
            enemies: List of detected hostile entities.
            priority_rule: Strategy rule ("servants_then_boss", "boss_only", "closest").

        Returns:
            NearbyEnemy or None: Primary target to aim at.
        """
        if not enemies:
            return None

        bosses = [e for e in enemies if e.is_boss]
        minions = [e for e in enemies if not e.is_boss]

        if priority_rule == "servants_then_boss":
            # If minions are within dangerous proximity (< 180 px), clear them first
            close_minions = [m for m in minions if m.distance < 180.0]
            if close_minions:
                return min(close_minions, key=lambda e: e.distance)
            if bosses:
                return bosses[0]
            return min(enemies, key=lambda e: e.distance)

        if priority_rule == "boss_only" and bosses:
            return bosses[0]

        # Default: closest enemy
        return min(enemies, key=lambda e: e.distance)

    def process_combat_tick(
        self,
        game_state: GameState,
        strategy: dict[str, Any],
        arena_bounds: tuple[int, int, int, int] | None = None,
    ) -> list[ActionCommand]:
        """Process one combat frame and generate immediate reflex action commands.

        Args:
            game_state: Live GameState snapshot.
            strategy: Loaded boss strategy dict from boss_strategies.yaml.
            arena_bounds: Optional arena bounding box (min_x, min_y, max_x, max_y) in tiles.

        Returns:
            list[ActionCommand]: Sequence of combat actions to dispatch.
        """
        commands: list[ActionCommand] = []
        player = game_state.player
        enemies = game_state.nearby_enemies

        if not enemies:
            return commands

        # 1. Evaluate Potion & Healing Needs
        hp_percent = (player.hp / player.max_hp) * 100.0
        heal_threshold = strategy.get("heal_hp_threshold_percent", 50.0)

        now = game_state.timestamp
        # Potion cooldown: minimum 60s between healing potions in Terraria (Potion Sickness)
        if hp_percent <= heal_threshold and (now - self.state.last_heal_tick > 60.0):
            commands.append(UsePotionCommand(potion_type="healing"))
            self.state.last_heal_tick = now

        # Check required buffs
        required_buffs = strategy.get("readiness_criteria", {}).get("required_buffs", [])
        active_buff_names = {b.name.lower() for b in player.buffs}
        missing_buffs = [b for b in required_buffs if b.lower() not in active_buff_names]

        if missing_buffs and (now - self.state.last_buff_tick > 30.0):
            commands.append(UsePotionCommand(potion_type="buff"))
            self.state.last_buff_tick = now

        # 2. Select Priority Target & Lead Aim
        target = self.select_priority_target(enemies)
        if target is not None:
            aim_x, aim_y = calculate_lead_aim(
                player_x=player.x,
                player_y=player.y,
                target_x=target.x,
                target_y=target.y,
                target_vx=target.velocity_x,
                target_vy=target.velocity_y,
                projectile_speed=15.0,
            )

            # Weapon slot selection: Slot 0 = Primary Ranged/Magic, Slot 1 = Melee Defense
            use_slot = 1 if target.distance < 60.0 else 0
            commands.append(
                AttackCommand(
                    aim_x=aim_x,
                    aim_y=aim_y,
                    use_item_slot=use_slot,
                    continuous=True,
                )
            )

        # 3. Kiting Pattern Execution
        patterns = strategy.get("combat_patterns", {})
        boss = next((e for e in enemies if e.is_boss), enemies[0])

        # Determine phase based on boss health
        boss_hp_percent = (boss.hp / boss.max_hp) * 100.0
        current_pattern = "horizontal_run"
        ideal_dist = 250.0

        if boss_hp_percent <= 50.0 and "phase_2" in patterns:
            current_pattern = patterns["phase_2"].get("pattern", "horizontal_run")
            ideal_dist = patterns["phase_2"].get("ideal_distance_px", 350.0)
        elif "phase_1" in patterns:
            current_pattern = patterns["phase_1"].get("pattern", "circle_kite")
            ideal_dist = patterns["phase_1"].get("ideal_distance_px", 250.0)

        # Execute Movement Pattern
        if current_pattern == "circle_kite":
            move_x, move_y = calculate_circle_kite_target(
                player_x=player.x,
                player_y=player.y,
                boss_x=boss.x,
                boss_y=boss.y,
                ideal_distance=ideal_dist,
                clockwise=True,
            )
            commands.append(
                MoveCommand(
                    target_x=move_x,
                    target_y=move_y,
                    duration_ms=100,
                )
            )
        else:
            # Horizontal Run across Arena
            # Convert arena tile bounds to pixels (1 tile = 16 pixels)
            if arena_bounds:
                arena_min_px = arena_bounds[0] * 16.0
                arena_max_px = arena_bounds[2] * 16.0
            else:
                arena_min_px = player.x - 800.0
                arena_max_px = player.x + 800.0

            move_x, move_y, self.state.moving_right = calculate_horizontal_run_target(
                player_x=player.x,
                player_y=player.y,
                arena_min_x=arena_min_px,
                arena_max_x=arena_max_px,
                moving_right=self.state.moving_right,
            )
            commands.append(
                MoveCommand(
                    target_x=move_x,
                    target_y=move_y,
                    duration_ms=150,
                )
            )

        return commands
