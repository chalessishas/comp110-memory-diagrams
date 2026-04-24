from data.characters.jesica import make_jesica, _S1_TAG, _S1_DURATION, _S2_TAG, _S2_DURATION


def test_jesica_s1_config():
    op = make_jesica(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.sp_cost == 3 and sk.initial_sp == 0
    assert sk.duration == _S1_DURATION and sk.behavior_tag == _S1_TAG
    assert sk.sp == 0.0


def test_jesica_s2_config():
    op = make_jesica(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.sp_cost == 35 and sk.initial_sp == 18
    assert sk.duration == _S2_DURATION and sk.behavior_tag == _S2_TAG
    assert sk.sp == 18.0
