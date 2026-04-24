from data.characters.hodrer import make_hodrer, _S1_TAG, _S1_DURATION, _S2_TAG, _S2_DURATION, _S3_TAG, _S3_DURATION


def test_hodrer_s1_config():
    op = make_hodrer(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.sp_cost == 3 and sk.initial_sp == 0
    assert sk.duration == _S1_DURATION and sk.behavior_tag == _S1_TAG
    assert sk.sp == 0.0


def test_hodrer_s2_config():
    op = make_hodrer(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.sp_cost == 40 and sk.initial_sp == 20
    assert sk.duration == _S2_DURATION and sk.behavior_tag == _S2_TAG
    assert sk.sp == 20.0


def test_hodrer_s3_config():
    op = make_hodrer(slot="S3")
    sk = op.skill
    assert sk is not None and sk.slot == "S3"
    assert sk.sp_cost == 55 and sk.initial_sp == 28
    assert sk.duration == _S3_DURATION and sk.behavior_tag == _S3_TAG
    assert sk.sp == 28.0
