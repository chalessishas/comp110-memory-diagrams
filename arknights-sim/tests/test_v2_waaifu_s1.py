import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


from data.characters.waaifu import make_waaifu, _S1_TAG, _S1_DURATION, _S2_TAG, _S2_DURATION

def test_waaifu_s1_config():
    op = make_waaifu(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.sp_cost == 5 and sk.initial_sp == 0
    assert sk.duration == _S1_DURATION and sk.behavior_tag == _S1_TAG
    assert sk.sp == 0.0

def test_waaifu_s2_config():
    op = make_waaifu(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.sp_cost == 35 and sk.initial_sp == 18
    assert sk.duration == _S2_DURATION and sk.behavior_tag == _S2_TAG
    assert sk.sp == 18.0
