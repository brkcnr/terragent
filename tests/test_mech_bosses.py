"""Unit tests for Mechanical Boss strategies and target priorities (Milestone 5 Scope)."""

from pathlib import Path

import yaml
from terragent.combat import CombatEngine
from terragent.schemas import NearbyEnemy


def test_mech_bosses_yaml_strategies_loaded() -> None:
    """Verify YAML configuration defines all 3 Mechanical Boss strategies."""
    config_path = Path(__file__).resolve().parent.parent / "configs" / "boss_strategies.yaml"
    with open(config_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert "the_destroyer" in data
    assert "the_twins" in data
    assert "skeletron_prime" in data

    destroyer = data["the_destroyer"]
    assert destroyer["arena"]["type"] == "high_elevation_box"
    assert destroyer["readiness_criteria"]["min_defense"] >= 45

    twins = data["the_twins"]
    assert twins["readiness_criteria"]["has_wings"] is True
    assert twins["combat_patterns"]["phase_1"]["target_priority"] == "spazmatism_first"

    prime = data["skeletron_prime"]
    assert prime["readiness_criteria"]["has_wings"] is True


def test_mech_boss_target_priority_probes() -> None:
    """Test prioritizing Destroyer probes to secure heart drops and avoid laser swarms."""
    engine = CombatEngine()

    enemies = [
        NearbyEnemy(
            enemy_id=134,
            name="The Destroyer",
            hp=80000,
            max_hp=80000,
            x=500.0,
            y=1000.0,
            distance=500.0,
            is_boss=True,
        ),
        NearbyEnemy(
            enemy_id=139,
            name="Probe",
            hp=200,
            max_hp=200,
            x=500.0,
            y=550.0,
            distance=80.0,  # Close probe < 180px
            is_boss=False,
        ),
    ]

    target = engine.select_priority_target(enemies, priority_rule="servants_then_boss")
    assert target is not None
    assert target.name == "Probe"
