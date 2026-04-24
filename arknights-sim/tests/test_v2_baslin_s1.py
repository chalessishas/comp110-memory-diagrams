"""Bassline (baslin) S1/S2 — both stub skills.

Tests cover:
  - S1 config (sp_cost=5, initial_sp=0, instant, AUTO_TIME AUTO)
  - S2 slot regression (default, duration=60s)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.characters.baslin import make_baslin, _S1_TAG, _S1_DURATION, _S2_TAG, _S2_DURATION


def test_baslin_s1_config():
    op = make_baslin(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.sp_cost == 5
    assert sk.initial_sp == 0
    assert sk.duration == _S1_DURATION
    assert sk.behavior_tag == _S1_TAG


def test_s2_slot_config():
    op = make_baslin(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.duration == _S2_DURATION
    assert sk.behavior_tag == _S2_TAG
