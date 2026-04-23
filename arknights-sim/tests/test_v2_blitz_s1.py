"""Blitz S1/S2 — both stub skills.

Tests cover:
  - S1 config (name, sp_cost=18, initial_sp=10, duration=3.5s)
  - S2 slot regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.characters.blitz import make_blitz, _S1_TAG, _S1_DURATION, _S2_TAG


def test_blitz_s1_config():
    op = make_blitz(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Flash Shield"
    assert sk.sp_cost == 18
    assert sk.initial_sp == 10
    assert sk.duration == _S1_DURATION
    assert sk.behavior_tag == _S1_TAG


def test_s2_slot_config():
    op = make_blitz(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Shield Bash"
    assert sk.behavior_tag == _S2_TAG
