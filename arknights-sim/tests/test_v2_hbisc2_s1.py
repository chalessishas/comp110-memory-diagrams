from data.characters.hbisc2 import make_hbisc2, _S1_TAG, _S1_DURATION, _S2_TAG, _S2_DURATION, _S3_TAG, _S3_DURATION


def test_hbisc2_s1_config():
    op = make_hbisc2(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.sp_cost == 6 and sk.initial_sp == 0
    assert sk.duration == _S1_DURATION and sk.behavior_tag == _S1_TAG
    assert sk.sp == 0.0


def test_hbisc2_s2_config():
    op = make_hbisc2(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.sp_cost == 50 and sk.initial_sp == 25
    assert sk.duration == _S2_DURATION and sk.behavior_tag == _S2_TAG
    assert sk.sp == 25.0


def test_hbisc2_s3_config():
    op = make_hbisc2(slot="S3")
    sk = op.skill
    assert sk is not None and sk.slot == "S3"
    assert sk.sp_cost == 70 and sk.initial_sp == 35
    assert sk.duration == _S3_DURATION and sk.behavior_tag == _S3_TAG
    assert sk.sp == 35.0
