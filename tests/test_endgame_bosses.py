"""Unit tests for Endgame boss configurations and strategy parameters (M6 Scope)."""

from pathlib import Path

import yaml


def test_endgame_bosses_yaml_loaded() -> None:
    """Verify boss_strategies.yaml contains all endgame bosses and pillars."""
    config_path = Path(__file__).resolve().parent.parent / "configs" / "boss_strategies.yaml"
    with open(config_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert "plantera" in data
    assert "golem" in data
    assert "lunatic_cultist" in data
    assert "celestial_pillars" in data
    assert "moon_lord" in data

    plantera = data["plantera"]
    assert plantera["arena"]["type"] == "excavated_jungle_box"
    assert plantera["readiness_criteria"]["has_wings"] is True

    golem = data["golem"]
    assert golem["readiness_criteria"]["min_defense"] >= 60

    cultist = data["lunatic_cultist"]
    assert cultist["combat_patterns"]["phase_1"]["target_priority"] == "real_cultist_no_duplicates"

    pillars = data["celestial_pillars"]
    assert "solar_pillar" in pillars
    assert pillars["solar_pillar"]["stay_grounded"] is True
    assert pillars["solar_pillar"]["avoid_crawltipede_air"] is True

    moon_lord = data["moon_lord"]
    assert moon_lord["arena"]["type"] == "long_asphalt_skyway_with_overhead_roof"
    assert moon_lord["readiness_criteria"]["min_defense"] >= 70
