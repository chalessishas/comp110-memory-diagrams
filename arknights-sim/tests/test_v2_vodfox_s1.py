import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.characters.vodfox import make_vodfox, _S1_TAG, _S1_DURATION, _S2_TAG, _S2_DURATION


def test_vodfox_s1_config():
    op = make_vodfox(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.sp_cost == 15 and sk.initial_sp == 8
    assert sk.duration == _S1_DURATION and sk.behavior_tag == _S1_TAG
    assert sk.sp == 8.0


def test_vodfox_s2_config():
    op = make_vodfox(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.sp_cost == 25 and sk.initial_sp == 12
    assert sk.duration == _S2_DURATION and sk.behavior_tag == _S2_TAG
    assert sk.sp == 12.0

