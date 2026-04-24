"""Glassb (glassb) S1/S2 — both stub skills."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from data.characters.glassb import make_glassb, _S1_TAG, _S1_DURATION, _S2_TAG

def test_glassb_s1_config():
    op = make_glassb(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.sp_cost == 20 and sk.initial_sp == 10
    assert sk.duration == _S1_DURATION and sk.behavior_tag == _S1_TAG

def test_s2_slot_config():
    op = make_glassb(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2" and sk.behavior_tag == _S2_TAG
