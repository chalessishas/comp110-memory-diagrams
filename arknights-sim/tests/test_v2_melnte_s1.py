"""Melanite (melnte) S1 behavior / S2 stub — Saturated Pulse ATK+160%."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from data.characters.melnte import make_melnte, _S1_TAG, _S1_DURATION, _S2_TAG, _S2_DURATION

def test_melnte_s1_config():
    op = make_melnte(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.sp_cost == 40 and sk.initial_sp == 20
    assert sk.duration == _S1_DURATION and sk.behavior_tag == _S1_TAG
    assert sk.sp == 20.0

def test_melnte_s2_config():
    op = make_melnte(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.sp_cost == 18 and sk.initial_sp == 6
    assert sk.duration == _S2_DURATION and sk.behavior_tag == _S2_TAG
    assert sk.sp == 6.0
