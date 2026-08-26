"""Unit tests for Hardmode Wings acquisition manager (Milestone 5 Scope)."""

from terragent.wings import (
    ITEM_GIANT_HARPY_FEATHER,
    ITEM_HARPY_WINGS,
    ITEM_SOUL_OF_FLIGHT,
    WingsManager,
)


def test_wings_equipped_detection() -> None:
    """Test detecting equipped wing accessory."""
    mgr = WingsManager()

    assert mgr.is_wings_equipped({100, 200, 300}) is False
    assert mgr.is_wings_equipped({100, ITEM_HARPY_WINGS, 300}) is True


def test_wings_crafting_materials_check() -> None:
    """Test checking materials for Harpy Wings."""
    mgr = WingsManager()

    # Case 1: Incomplete materials
    can_craft_1, msg_1 = mgr.can_craft_harpy_wings({ITEM_SOUL_OF_FLIGHT: 12})
    assert can_craft_1 is False
    assert "8 Soul of Flight" in msg_1
    assert "Giant Harpy Feather" in msg_1

    # Case 2: Complete materials
    can_craft_2, msg_2 = mgr.can_craft_harpy_wings(
        {
            ITEM_SOUL_OF_FLIGHT: 20,
            ITEM_GIANT_HARPY_FEATHER: 1,
        }
    )
    assert can_craft_2 is True
    assert "Ready to craft" in msg_2


def test_wings_purchase_conditions() -> None:
    """Test Leaf Wings purchase criteria from Witch Doctor."""
    mgr = WingsManager()

    # Case 1: Not in jungle
    can_p1, msg_p1 = mgr.can_purchase_leaf_wings(
        total_coins=2_000_000,
        in_jungle_biome=False,
        is_night=True,
    )
    assert can_p1 is False
    assert "Jungle" in msg_p1

    # Case 2: Daytime
    can_p2, msg_p2 = mgr.can_purchase_leaf_wings(
        total_coins=2_000_000,
        in_jungle_biome=True,
        is_night=False,
    )
    assert can_p2 is False
    assert "nighttime" in msg_p2

    # Case 3: Insufficient coins
    can_p3, msg_p3 = mgr.can_purchase_leaf_wings(
        total_coins=500_000,
        in_jungle_biome=True,
        is_night=True,
    )
    assert can_p3 is False
    assert "Insufficient funds" in msg_p3

    # Case 4: All conditions met
    can_p4, msg_p4 = mgr.can_purchase_leaf_wings(
        total_coins=1_000_000,
        in_jungle_biome=True,
        is_night=True,
    )
    assert can_p4 is True
    assert "Ready to purchase" in msg_p4
