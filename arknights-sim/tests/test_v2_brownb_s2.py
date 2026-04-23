"""Beehunter (brownb) S1/S2.

S1 is a passive dodge (no SkillComponent).
S2 "Soaring Fists" — stub (attack interval −55% ratio; no sim precedent for RATIO on ATK_INTERVAL).

Tests cover:
  - S2 config (name, sp_cost=30, initial_sp=0, duration=10s)
  - S1 slot returns no skill (passive has no SkillComponent)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.characters.brownb import make_brownb, _S2_TAG, _S2_DURATION


def test_brownb_s2_config():
    op = make_brownb(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Soaring Fists"
    assert sk.sp_cost == 30
    assert sk.initial_sp == 0
    assert sk.duration == _S2_DURATION
    assert sk.behavior_tag == _S2_TAG


def test_brownb_s1_no_skill():
    op = make_brownb(slot="S1")
    assert op.skill is None
