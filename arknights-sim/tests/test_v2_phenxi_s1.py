"""Fiammetta (phenxi) S1 behavior / S2+S3 stubs — Provocate ATK+60%."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from data.characters.phenxi import make_phenxi, _S1_TAG, _S1_DURATION, _S2_TAG, _S2_DURATION, _S3_TAG, _S3_DURATION

def test_phenxi_s1_config():
    op = make_phenxi(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.sp_cost == 14 and sk.initial_sp == 5
    assert sk.duration == _S1_DURATION and sk.behavior_tag == _S1_TAG
    assert sk.sp == 5.0

def test_phenxi_s2_config():
    op = make_phenxi(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.sp_cost == 10 and sk.initial_sp == 0
    assert sk.duration == _S2_DURATION and sk.behavior_tag == _S2_TAG
    assert sk.sp == 0.0

def test_phenxi_s3_config():
    op = make_phenxi(slot="S3")
    sk = op.skill
    assert sk is not None and sk.slot == "S3"
    assert sk.sp_cost == 19 and sk.initial_sp == 0
    assert sk.duration == _S3_DURATION and sk.behavior_tag == _S3_TAG
    assert sk.sp == 0.0
