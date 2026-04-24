import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


from data.characters.zuole import make_zuole, _S1_TAG, _S1_DURATION, _S2_TAG, _S2_DURATION, _S3_TAG, _S3_DURATION

def test_zuole_s1_config():
    op = make_zuole(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.sp_cost == 8 and sk.initial_sp == 4
    assert sk.duration == _S1_DURATION and sk.behavior_tag == _S1_TAG
    assert sk.sp == 4.0

def test_zuole_s2_config():
    op = make_zuole(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.sp_cost == 40 and sk.initial_sp == 20
    assert sk.duration == _S2_DURATION and sk.behavior_tag == _S2_TAG
    assert sk.sp == 20.0

def test_zuole_s3_config():
    op = make_zuole(slot="S3")
    sk = op.skill
    assert sk is not None and sk.slot == "S3"
    assert sk.sp_cost == 65 and sk.initial_sp == 32
    assert sk.duration == _S3_DURATION and sk.behavior_tag == _S3_TAG
    assert sk.sp == 32.0
