import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


from data.characters.whitw2 import make_whitw2, _S1_TAG, _S1_DURATION, _S2_TAG, _S2_DURATION

def test_whitw2_s1_config():
    op = make_whitw2(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.sp_cost == 5 and sk.initial_sp == 0
    assert sk.duration == _S1_DURATION and sk.behavior_tag == _S1_TAG
    assert sk.sp == 0.0

def test_whitw2_s2_config():
    op = make_whitw2(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.sp_cost == 25 and sk.initial_sp == 12
    assert sk.duration == _S2_DURATION and sk.behavior_tag == _S2_TAG
    assert sk.sp == 12.0
