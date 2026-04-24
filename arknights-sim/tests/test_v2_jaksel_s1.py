"""Jackie (Jaksel) — 4★ GUARD_FIGHTER, S1/S2 config tests."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.types import RoleArchetype
from data.characters.jaksel import make_jaksel, _S1_TAG, _S1_DURATION, _S2_TAG, _S2_DURATION


def test_jaksel_archetype():
    op = make_jaksel()
    assert op.archetype == RoleArchetype.GUARD_FIGHTER


def test_jaksel_s1_config():
    op = make_jaksel(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.sp_cost == 3 and sk.initial_sp == 0
    assert sk.duration == _S1_DURATION and sk.behavior_tag == _S1_TAG
    assert sk.sp == 0.0


def test_jaksel_s2_config():
    op = make_jaksel(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Pay Close Attention!"
    assert sk.sp_cost == 35 and sk.initial_sp == 15
    assert sk.duration == _S2_DURATION and sk.behavior_tag == _S2_TAG
    assert sk.sp == 15.0
