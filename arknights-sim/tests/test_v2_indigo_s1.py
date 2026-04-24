from data.characters.indigo import make_indigo, _S1_TAG, _S1_DURATION, _S2_TAG, _S2_DURATION, _S3_TAG, _S3_DURATION


def test_indigo_s1_config():
    op = make_indigo(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.sp_cost == 20 and sk.initial_sp == 10
    assert sk.duration == _S1_DURATION and sk.behavior_tag == _S1_TAG
    assert sk.sp == 10.0


def test_indigo_s2_config():
    op = make_indigo(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.sp_cost == 45 and sk.initial_sp == 22
    assert sk.duration == _S2_DURATION and sk.behavior_tag == _S2_TAG
    assert sk.sp == 22.0


def test_indigo_s3_config():
    op = make_indigo(slot="S3")
    sk = op.skill
    assert sk is not None and sk.slot == "S3"
    assert sk.sp_cost == 60 and sk.initial_sp == 30
    assert sk.duration == _S3_DURATION and sk.behavior_tag == _S3_TAG
    assert sk.sp == 30.0
