"""Unit tests for Hardmode state transition manager (Milestone 4 Scope)."""

from terragent.hardmode import ITEM_PWNHAMMER, HardmodeManager
from terragent.schemas import GameState, PlayerState


def test_hardmode_transition_pre_hardmode() -> None:
    """Test Pre-Hardmode world state evaluation."""
    mgr = HardmodeManager()

    state = GameState(
        protocol_version="1.0.0",
        timestamp=100.0,
        player=PlayerState(hp=300, max_hp=300, x=100.0, y=100.0),
        is_hardmode=False,
    )
    status = mgr.evaluate_transition(state, owned_item_ids=set())

    assert status.is_hardmode is False
    assert status.has_pwnhammer is False
    assert status.transition_ready_for_m5 is False


def test_hardmode_transition_wof_defeated() -> None:
    """Test Hardmode activation upon Wall of Flesh defeat and Pwnhammer acquisition."""
    mgr = HardmodeManager()

    # Step 1: Hardmode active, but hammer not yet picked up
    state = GameState(
        protocol_version="1.0.0",
        timestamp=200.0,
        player=PlayerState(hp=280, max_hp=300, x=2000.0, y=3200.0),
        is_hardmode=True,
    )
    status_step1 = mgr.evaluate_transition(state, owned_item_ids=set())
    assert status_step1.is_hardmode is True
    assert status_step1.has_pwnhammer is False
    assert status_step1.safety_quarantine_active is True
    assert status_step1.transition_ready_for_m5 is False

    # Step 2: Hammer collected -> Ready for M5
    status_step2 = mgr.evaluate_transition(state, owned_item_ids={ITEM_PWNHAMMER})
    assert status_step2.is_hardmode is True
    assert status_step2.has_pwnhammer is True
    assert status_step2.transition_ready_for_m5 is True
