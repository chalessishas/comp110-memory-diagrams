"""Bstalk (Beanstalk) S1/S2 — both stub skills.

Tests cover:
  - S1 config (name, sp_cost=34, initial_sp=11)
  - S2 slot regression (sp_cost=44, initial_sp=14)
  - Archetype VAN_TACTICIAN
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.types import RoleArchetype
from data.characters.bstalk import make_bstalk, _S1_TAG, _S1_DURATION, _S2_TAG


def test_bstalk_config():
    op = make_bstalk(slot="S1")
    assert op.archetype == RoleArchetype.VAN_TACTICIAN


def test_bstalk_s1_config():
    op = make_bstalk(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Sentinel Command"
    assert sk.sp_cost == 34
    assert sk.initial_sp == 11
    assert sk.duration == _S1_DURATION
    assert sk.behavior_tag == _S1_TAG


def test_s2_slot_config():
    op = make_bstalk(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "'Everyone Together!'"
    assert sk.sp_cost == 44
    assert sk.initial_sp == 14
    assert sk.behavior_tag == _S2_TAG
