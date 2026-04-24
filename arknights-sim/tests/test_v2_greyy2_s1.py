"""Greyy the Lightchaser (greyy2) S1/S2/S3 — all stub skills."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from data.characters.greyy2 import make_greyy2, _S1_TAG, _S1_DURATION, _S2_TAG, _S3_TAG

def test_greyy2_s1_config():
    op = make_greyy2(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.sp_cost == 4 and sk.initial_sp == 0
    assert sk.duration == _S1_DURATION and sk.behavior_tag == _S1_TAG

def test_s2_slot_config():
    op = make_greyy2(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2" and sk.behavior_tag == _S2_TAG

def test_s3_slot_config():
    op = make_greyy2(slot="S3")
    sk = op.skill
    assert sk is not None and sk.slot == "S3" and sk.behavior_tag == _S3_TAG
