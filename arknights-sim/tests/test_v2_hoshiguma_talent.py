"""Hoshiguma talent: Overweight — 20% damage reduction when HP > 50%."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.state.unit_state import TalentComponent
from data.characters.hoshiguma import make_hoshiguma


def test_overweight_reduces_damage_above_half_hp():
    """Hoshiguma takes 20% less damage when above 50% HP."""
    hoshi = make_hoshiguma()
    assert hoshi.hp / hoshi.max_hp > 0.5, "Should start above 50% HP"

    # Take 1000 raw damage directly (bypassing physical DEF for clarity)
    hp_before = hoshi.hp
    actual = hoshi.take_damage(1000)

    expected = int(1000 * 0.80)   # 20% reduction
    assert actual == max(1, expected), \
        f"Damage should be reduced 20% to {expected}, got {actual}"
    assert hoshi.hp == hp_before - actual


def test_overweight_inactive_below_half_hp():
    """Hoshiguma takes full damage when HP drops to ≤ 50%."""
    hoshi = make_hoshiguma()
    # Drop HP to exactly 50% (at or below threshold)
    hoshi.hp = hoshi.max_hp // 2

    hp_before = hoshi.hp
    actual = hoshi.take_damage(1000)

    assert actual == max(1, 1000), \
        f"No reduction below 50% HP — expected 1000, got {actual}"


def test_overweight_talent_wired_on_make_hoshiguma():
    """make_hoshiguma() must include the Overweight talent component."""
    hoshi = make_hoshiguma()
    tags = [t.behavior_tag for t in hoshi.talents]
    assert "hoshiguma_overweight" in tags, \
        f"Overweight talent not in {tags}"
    overweight = next(t for t in hoshi.talents if t.behavior_tag == "hoshiguma_overweight")
    assert overweight.params["reduction"] == 0.20
    assert overweight.params["hp_threshold"] == 0.5
