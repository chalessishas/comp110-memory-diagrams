"""Dorothy (doroth) S1/S2 — both stub skills.

Tests cover:
  - S1 config (sp_cost=30, initial_sp=15, AUTO_TIME MANUAL)
  - S2 slot regression (default)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.characters.doroth import make_doroth, _S1_TAG, _S1_DURATION, _S2_TAG


def test_doroth_s1_config():
    op = make_doroth(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.sp_cost == 30
    assert sk.initial_sp == 15
    assert sk.duration == _S1_DURATION
    assert sk.behavior_tag == _S1_TAG


def test_s2_slot_config():
    op = make_doroth(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.behavior_tag == _S2_TAG
