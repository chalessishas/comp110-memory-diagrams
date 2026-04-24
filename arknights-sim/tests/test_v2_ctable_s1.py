"""Cantabile (ctable) S1/S2 — both stub skills.

Tests cover:
  - S1 config (sp_cost=0, initial_sp=0, duration=17s, ON_DEPLOY AUTO)
  - S2 slot regression (default)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.characters.ctable import make_ctable, _S1_TAG, _S1_DURATION, _S2_TAG


def test_ctable_s1_config():
    op = make_ctable(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.sp_cost == 0
    assert sk.initial_sp == 0
    assert sk.duration == _S1_DURATION
    assert sk.behavior_tag == _S1_TAG


def test_s2_slot_config():
    op = make_ctable(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.behavior_tag == _S2_TAG
