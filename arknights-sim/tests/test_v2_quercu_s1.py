import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.characters.quercu import make_quercu, _S1_TAG, _S1_DURATION, _S2_TAG, _S2_DURATION


def test_quercu_s1_config():
    op = make_quercu(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.sp_cost == 20 and sk.initial_sp == 10
    assert sk.duration == _S1_DURATION and sk.behavior_tag == _S1_TAG
    assert sk.sp == 10.0


def test_quercu_s2_config():
    op = make_quercu(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.sp_cost == 30 and sk.initial_sp == 15
    assert sk.duration == _S2_DURATION and sk.behavior_tag == _S2_TAG
    assert sk.sp == 15.0
