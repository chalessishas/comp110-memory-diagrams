"""Ardign (Cardigan) S1 "Regeneration α" — instant heal stub.

Tests cover:
  - S1 config (name, sp_cost=20, initial_sp=10, duration=0s, MANUAL)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.characters.ardign import make_ardign, _S1_TAG, _S1_DURATION


def test_ardign_s1_config():
    op = make_ardign(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Regeneration α"
    assert sk.sp_cost == 20
    assert sk.initial_sp == 10
    assert sk.duration == _S1_DURATION
    assert sk.behavior_tag == _S1_TAG
