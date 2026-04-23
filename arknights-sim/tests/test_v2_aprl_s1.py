"""April (aprl) S1/S2 — both stub skills.

Tests cover:
  - S1 config (name, sp_cost=4, initial_sp=0)
  - S2 slot regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.characters.aprl import make_aprl, _S1_TAG, _S1_DURATION, _S2_TAG


def test_aprl_s1_config():
    op = make_aprl(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Precise Shooting"
    assert sk.sp_cost == 4
    assert sk.initial_sp == 0
    assert sk.duration == _S1_DURATION
    assert sk.behavior_tag == _S1_TAG


def test_s2_slot_config():
    op = make_aprl(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Flexible Camouflage"
    assert sk.behavior_tag == _S2_TAG
