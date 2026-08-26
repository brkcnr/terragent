"""Unit tests for reflex combat engine and kiting controllers (Milestone 3 Scope)."""

import math

from terragent.combat import (
    CombatEngine,
    calculate_circle_kite_target,
    calculate_horizontal_run_target,
    calculate_lead_aim,
)
from terragent.schemas import (
    AttackCommand,
    BuffState,
    GameState,
    MoveCommand,
    NearbyEnemy,
    PlayerState,
    UsePotionCommand,
)


def test_calculate_lead_aim_stationary() -> None:
    """Test aiming directly at stationary target."""
    aim_x, aim_y = calculate_lead_aim(
        player_x=100.0,
        player_y=100.0,
        target_x=300.0,
        target_y=100.0,
        target_vx=0.0,
        target_vy=0.0,
    )
    assert aim_x == 300.0
    assert aim_y == 100.0


def test_calculate_lead_aim_moving_target() -> None:
    """Test predictive aim calculation for moving enemy."""
    aim_x, aim_y = calculate_lead_aim(
        player_x=0.0,
        player_y=0.0,
        target_x=100.0,
        target_y=0.0,
        target_vx=5.0,  # Moving right at 5 px/frame
        target_vy=0.0,
        projectile_speed=10.0,  # 10 frames travel time
    )
    # Target travels 5 * 10 = 50 px -> predicted X = 150
    assert aim_x == 150.0
    assert aim_y == 0.0


def test_circle_kite_target_radius() -> None:
    """Test orbital kiting target maintains desired radius."""
    boss_x, boss_y = 500.0, 500.0
    ideal_radius = 250.0

    target_x, target_y = calculate_circle_kite_target(
        player_x=750.0,
        player_y=500.0,
        boss_x=boss_x,
        boss_y=boss_y,
        ideal_distance=ideal_radius,
    )

    dist = math.hypot(target_x - boss_x, target_y - boss_y)
    assert math.isclose(dist, ideal_radius, rel_tol=1e-3)


def test_horizontal_run_turnaround() -> None:
    """Test linear sprint turns around when reaching arena boundaries."""
    # Moving right towards right boundary (1000px)
    _, _, moving_right = calculate_horizontal_run_target(
        player_x=950.0,
        player_y=200.0,
        arena_min_x=0.0,
        arena_max_x=1000.0,
        moving_right=True,
        margin_px=100.0,
    )
    assert moving_right is False  # Reached margin -> reversed to left

    # Moving left towards left boundary (0px)
    _, _, moving_right_2 = calculate_horizontal_run_target(
        player_x=50.0,
        player_y=200.0,
        arena_min_x=0.0,
        arena_max_x=1000.0,
        moving_right=False,
        margin_px=100.0,
    )
    assert moving_right_2 is True  # Reached margin -> reversed to right


def test_combat_engine_tick_execution() -> None:
    """Test CombatEngine processing state and emitting attack, move, and heal actions."""
    engine = CombatEngine()

    state = GameState(
        protocol_version="1.0.0",
        timestamp=100.0,
        player=PlayerState(
            hp=60,  # 30% HP -> should trigger heal
            max_hp=200,
            defense=14,
            x=500.0,
            y=300.0,
            selected_slot=0,
            buffs=[BuffState(buff_id=5, name="Ironskin", duration_seconds=120.0)],
        ),
        nearby_enemies=[
            NearbyEnemy(
                enemy_id=4,
                name="Eye of Cthulhu",
                hp=1400,
                max_hp=2800,
                x=700.0,
                y=250.0,
                velocity_x=-3.0,
                velocity_y=1.0,
                distance=206.0,
                is_boss=True,
            ),
            NearbyEnemy(
                enemy_id=5,
                name="Servant of Cthulhu",
                hp=8,
                max_hp=8,
                x=550.0,
                y=300.0,
                distance=50.0,  # Close minion < 180px -> priority target
                is_boss=False,
            ),
        ],
    )

    strategy = {
        "heal_hp_threshold_percent": 50.0,
        "readiness_criteria": {
            "required_buffs": ["Ironskin", "Regeneration", "Swiftness"],
        },
        "combat_patterns": {
            "phase_1": {"pattern": "circle_kite", "ideal_distance_px": 250.0},
        },
    }

    commands = engine.process_combat_tick(state, strategy)
    assert len(commands) >= 3

    # Check for Healing potion command
    heal_cmds = [
        c for c in commands if isinstance(c, UsePotionCommand) and c.potion_type == "healing"
    ]
    assert len(heal_cmds) == 1

    # Check for Buff potion command (missing Regeneration & Swiftness)
    buff_cmds = [c for c in commands if isinstance(c, UsePotionCommand) and c.potion_type == "buff"]
    assert len(buff_cmds) == 1

    # Check for Attack command targeting close minion with melee slot (distance 50 < 60)
    atk_cmds = [c for c in commands if isinstance(c, AttackCommand)]
    assert len(atk_cmds) == 1
    assert atk_cmds[0].use_item_slot == 1  # Melee slot for close defense

    # Check for Move command
    move_cmds = [c for c in commands if isinstance(c, MoveCommand)]
    assert len(move_cmds) == 1
