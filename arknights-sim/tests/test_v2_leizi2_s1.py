from data.characters.leizi2 import make_leizi2, _S1_TAG, _S1_DURATION, _S2_TAG, _S2_DURATION, _S3_TAG, _S3_DURATION


def test_leizi2_s1_config():
    op = make_leizi2(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.sp_cost == 5 and sk.initial_sp == 0
    assert sk.duration == _S1_DURATION and sk.behavior_tag == _S1_TAG
    assert sk.sp == 0.0


def test_leizi2_s2_config():
    op = make_leizi2(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.sp_cost == 50 and sk.initial_sp == 25
    assert sk.duration == _S2_DURATION and sk.behavior_tag == _S2_TAG
    assert sk.sp == 25.0


def test_leizi2_s3_config():
    op = make_leizi2(slot="S3")
    sk = op.skill
    assert sk is not None and sk.slot == "S3"
    assert sk.sp_cost == 65 and sk.initial_sp == 32
    assert sk.duration == _S3_DURATION and sk.behavior_tag == _S3_TAG
    assert sk.sp == 32.0
