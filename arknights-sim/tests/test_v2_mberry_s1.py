from data.characters.mberry import make_mberry, _S1_TAG, _S1_DURATION, _S2_TAG, _S2_DURATION


def test_mberry_s1_config():
    op = make_mberry(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.sp_cost == 9 and sk.initial_sp == 0
    assert sk.duration == _S1_DURATION and sk.behavior_tag == _S1_TAG
    assert sk.sp == 0.0


def test_mberry_s2_config():
    op = make_mberry(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.sp_cost == 40 and sk.initial_sp == 20
    assert sk.duration == _S2_DURATION and sk.behavior_tag == _S2_TAG
    assert sk.sp == 20.0
