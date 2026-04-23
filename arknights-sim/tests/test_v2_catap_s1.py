"""Catapult S1 "Blast Range Up α" — 30s MANUAL, splash_radius stub.

Tests cover:
  - S1 config (name, sp_cost=45, initial_sp=0, duration=30s)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.characters.catap import make_catap, _S1_TAG, _S1_DURATION


def test_catap_s1_config():
    op = make_catap(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Blast Range Up α"
    assert sk.sp_cost == 45
    assert sk.initial_sp == 0
    assert sk.duration == _S1_DURATION
    assert sk.behavior_tag == _S1_TAG
