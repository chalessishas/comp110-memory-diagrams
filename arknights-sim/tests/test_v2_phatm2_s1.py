from data.characters.phatm2 import make_phatm2, _S1_TAG, _S1_DURATION, _S2_TAG, _S2_DURATION


def test_phatm2_s1_config():
    op = make_phatm2(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.sp_cost == 15 and sk.initial_sp == 8
    assert sk.duration == _S1_DURATION and sk.behavior_tag == _S1_TAG
    assert sk.sp == 8.0


def test_phatm2_s2_config():
    op = make_phatm2(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.sp_cost == 35 and sk.initial_sp == 18
    assert sk.duration == _S2_DURATION and sk.behavior_tag == _S2_TAG
    assert sk.sp == 18.0
