from data.characters.ju import make_ju, _S1_TAG, _S1_DURATION, _S2_TAG, _S2_DURATION


def test_ju_s1_config():
    op = make_ju(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.sp_cost == 3 and sk.initial_sp == 0
    assert sk.duration == _S1_DURATION and sk.behavior_tag == _S1_TAG
    assert sk.sp == 0.0


def test_ju_s2_config():
    op = make_ju(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.sp_cost == 45 and sk.initial_sp == 22
    assert sk.duration == _S2_DURATION and sk.behavior_tag == _S2_TAG
    assert sk.sp == 22.0
