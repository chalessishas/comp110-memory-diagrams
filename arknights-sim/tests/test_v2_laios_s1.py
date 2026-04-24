from data.characters.laios import make_laios, _S1_TAG, _S1_DURATION, _S2_TAG, _S2_DURATION


def test_laios_s1_config():
    op = make_laios(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.sp_cost == 0 and sk.initial_sp == 0
    assert sk.duration == _S1_DURATION and sk.behavior_tag == _S1_TAG
    assert sk.sp == 0.0


def test_laios_s2_config():
    op = make_laios(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.sp_cost == 22 and sk.initial_sp == 10
    assert sk.duration == _S2_DURATION and sk.behavior_tag == _S2_TAG
    assert sk.sp == 10.0
