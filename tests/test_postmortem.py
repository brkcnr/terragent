"""Unit tests for postmortem logging and failure diagnosis (Milestone 3 Scope)."""

from terragent.postmortem import PostmortemManager


def test_postmortem_recording_and_counts() -> None:
    """Test logging boss attempts and verifying attempt counts."""
    mgr = PostmortemManager(":memory:")

    assert mgr.get_attempt_count("eye_of_cthulhu") == 0

    id1 = mgr.record_attempt(
        boss_name="eye_of_cthulhu",
        outcome="defeat",
        duration_seconds=45.2,
        damage_dealt=1200,
        cause_of_death="High speed charge collision in Phase 2",
        gear_used={"armor": "Gold", "weapon": "Gold Bow"},
        strategy_notes="Player struggled to turn around in time during enraged charges",
    )
    assert id1 == 1
    assert mgr.get_attempt_count("eye_of_cthulhu") == 1

    id2 = mgr.record_attempt(
        boss_name="eye_of_cthulhu",
        outcome="victory",
        duration_seconds=82.0,
        damage_dealt=2800,
        cause_of_death=None,
        strategy_notes="Victory achieved with Swiftness potion and longer arena",
    )
    assert id2 == 2
    assert mgr.get_attempt_count("eye_of_cthulhu") == 2

    attempts = mgr.get_attempts("eye_of_cthulhu")
    assert len(attempts) == 2
    assert attempts[0]["outcome"] == "defeat"
    assert attempts[1]["outcome"] == "victory"


def test_postmortem_circuit_breaker_and_analysis() -> None:
    """Test circuit breaker flagging when attempts reach limit."""
    mgr = PostmortemManager(":memory:")

    # 3 consecutive failed attempts
    for _ in range(3):
        mgr.record_attempt(
            boss_name="eater_of_worlds",
            outcome="defeat",
            duration_seconds=30.0,
            damage_dealt=500,
            cause_of_death="Vile spit and head collision",
        )

    analysis = mgr.analyze_failures("eater_of_worlds", max_allowed_attempts=3)
    assert analysis["attempt_count"] == 3
    assert analysis["requires_human_review"] is True
    assert "Swiftness" in analysis["recommendation"] or "armor" in analysis["recommendation"]
