"""Unit tests for Altar smashing and Hardmode ore tiers (Milestone 5 Scope)."""

from terragent.altar import AltarManager, HardmodeOreTier


def test_altar_ore_tier_progression() -> None:
    """Test unlocking ore tiers progressively as altars are smashed."""
    mgr = AltarManager(altars_broken=0)
    assert mgr.get_unlocked_tiers() == []

    mgr.record_altar_broken(1)
    assert mgr.get_unlocked_tiers() == [HardmodeOreTier.TIER_1_COBALT_PALLADIUM]

    mgr.record_altar_broken(1)
    assert mgr.get_unlocked_tiers() == [
        HardmodeOreTier.TIER_1_COBALT_PALLADIUM,
        HardmodeOreTier.TIER_2_MYTHRIL_ORICHALCUM,
    ]

    mgr.record_altar_broken(1)
    assert mgr.get_unlocked_tiers() == [
        HardmodeOreTier.TIER_1_COBALT_PALLADIUM,
        HardmodeOreTier.TIER_2_MYTHRIL_ORICHALCUM,
        HardmodeOreTier.TIER_3_ADAMANTITE_TITANIUM,
    ]


def test_altar_breaking_plan() -> None:
    """Test generating BreakTileCommands for target quota of altars."""
    mgr = AltarManager(altars_broken=2)
    coords = [(500, 800), (520, 810), (540, 805), (560, 815), (580, 820)]

    # Target 6 total altars -> 4 needed
    cmds = mgr.plan_altar_breaking(coords, target_total_altars=6)
    assert len(cmds) == 4
    assert cmds[0].tile_x == 500
    assert cmds[3].tile_x == 560
