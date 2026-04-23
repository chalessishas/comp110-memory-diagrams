"""Blacknight (blkngt) S1/S2 — both stub skills.

Tests cover:
  - S1 config (name, sp_cost=28, initial_sp=14, duration=10s)
  - S2 slot regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.characters.blkngt import make_blkngt, _S1_TAG, _S1_DURATION, _S2_TAG


def test_blkngt_s1_config():
    op = make_blkngt(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Drowsy"
    assert sk.sp_cost == 28
    assert sk.initial_sp == 14
    assert sk.duration == _S1_DURATION
    assert sk.behavior_tag == _S1_TAG


def test_s2_slot_config():
    op = make_blkngt(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Peaceful Slumber"
    assert sk.behavior_tag == _S2_TAG
