"""Dobermann S1/S2 — both stub skills.

Tests cover:
  - S1 config (name, sp_cost=4, initial_sp=0)
  - S2 config (name, sp_cost=35, initial_sp=17, duration=25s)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.characters.doberm import make_doberm, _S1_TAG, _S1_DURATION, _S2_TAG, _S2_DURATION


def test_doberm_s1_config():
    op = make_doberm(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Power Strike β"
    assert sk.sp_cost == 4
    assert sk.initial_sp == 0
    assert sk.duration == _S1_DURATION
    assert sk.behavior_tag == _S1_TAG


def test_s2_slot_config():
    op = make_doberm(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Spur"
    assert sk.sp_cost == 35
    assert sk.initial_sp == 17
    assert sk.duration == _S2_DURATION
    assert sk.behavior_tag == _S2_TAG
