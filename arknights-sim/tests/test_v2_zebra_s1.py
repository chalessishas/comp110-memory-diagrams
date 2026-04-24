"""Zebra S1 stub regression — verifies slot config only; behavior not implemented."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.characters.zebra import make_zebra, _S1_TAG, _S1_DURATION, _S2_TAG, _S2_DURATION


def test_zebra_s1_config():
    op = make_zebra(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.sp_cost == 4 and sk.initial_sp == 0
    assert sk.duration == _S1_DURATION and sk.behavior_tag == _S1_TAG
    assert sk.sp == 0.0


def test_zebra_s2_slot_regression():
    op = make_zebra(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.behavior_tag == _S2_TAG
