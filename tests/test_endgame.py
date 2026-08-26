"""Unit tests for Endgame manager, pillar shields, and final run reporting (M6 Scope)."""

from terragent.endgame import EndgameManager


def test_endgame_pillar_shield_and_clearance() -> None:
    """Test pillar enemy kill counting, shield falling, and destruction tracking."""
    mgr = EndgameManager()
    assert mgr.are_all_pillars_cleared() is False

    # Solar pillar: 50 kills -> shield still up
    shield_down_50 = mgr.record_pillar_enemy_kill("solar", count=50)
    assert shield_down_50 is False

    # Solar pillar: +50 kills -> 100 total -> shield drops
    shield_down_100 = mgr.record_pillar_enemy_kill("solar", count=50)
    assert shield_down_100 is True

    # Mark all 4 pillars destroyed
    for p in ["solar", "vortex", "nebula", "stardust"]:
        mgr.mark_pillar_destroyed(p)

    assert mgr.are_all_pillars_cleared() is True


def test_moon_lord_readiness_evaluation() -> None:
    """Test evaluating gear, defense, and ammo for Moon Lord fight."""
    mgr = EndgameManager()

    # Case 1: Missing wings
    ready_1, msg_1 = mgr.evaluate_moon_lord_readiness(
        player_defense=75,
        has_wings=False,
        ammo_count=2000,
    )
    assert ready_1 is False
    assert "Wings" in msg_1

    # Case 2: Low defense
    ready_2, msg_2 = mgr.evaluate_moon_lord_readiness(
        player_defense=50,
        has_wings=True,
        ammo_count=2000,
    )
    assert ready_2 is False
    assert "defense" in msg_2

    # Case 3: Low ammo
    ready_3, msg_3 = mgr.evaluate_moon_lord_readiness(
        player_defense=75,
        has_wings=True,
        ammo_count=500,
    )
    assert ready_3 is False
    assert "Ammo" in msg_3

    # Case 4: Ready
    ready_4, msg_4 = mgr.evaluate_moon_lord_readiness(
        player_defense=75,
        has_wings=True,
        ammo_count=2000,
    )
    assert ready_4 is True
    assert "Ready" in msg_4


def test_final_run_report_generation() -> None:
    """Test compiling comprehensive playthrough run report."""
    mgr = EndgameManager()
    mgr.status.moon_lord_defeated = True
    for p in ["solar", "vortex", "nebula", "stardust"]:
        mgr.mark_pillar_destroyed(p)

    mock_history = [
        {"boss_name": "eye_of_cthulhu", "outcome": "victory"},
        {"boss_name": "eater_of_worlds", "outcome": "victory"},
        {"boss_name": "skeletron", "outcome": "victory"},
        {"boss_name": "wall_of_flesh", "outcome": "victory"},
        {"boss_name": "the_destroyer", "outcome": "victory"},
        {"boss_name": "the_twins", "outcome": "victory"},
        {"boss_name": "skeletron_prime", "outcome": "victory"},
        {"boss_name": "plantera", "outcome": "victory"},
        {"boss_name": "golem", "outcome": "victory"},
        {"boss_name": "lunatic_cultist", "outcome": "victory"},
        {"boss_name": "moon_lord", "outcome": "defeat"},
        {"boss_name": "moon_lord", "outcome": "victory"},
    ]

    report = mgr.generate_final_run_report(
        total_playtime_seconds=28800.0,  # 8 hours
        housed_npcs_count=8,
        categorized_chests_count=8,
        attempt_history=mock_history,
    )

    assert "VICTORY: Moon Lord Defeated" in report["run_status"]
    assert report["total_playtime"] == "08:00:00"
    assert report["progression_milestones"]["m6_endgame_moon_lord"] is True
    assert report["world_statistics"]["town_npcs_housed"] == 8
    assert report["boss_combat_metrics"]["total_attempts"] == 12
    assert report["boss_combat_metrics"]["total_victories"] == 11
    assert report["boss_combat_metrics"]["total_defeats"] == 1
