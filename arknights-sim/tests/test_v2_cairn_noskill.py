"""Cairn — no-skill Defender. Config-only tests."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.types import AttackType, Profession, RoleArchetype
from data.characters.cairn import make_cairn


def test_cairn_config():
    op = make_cairn()
    assert op.name == "Cairn"
    assert op.profession == Profession.DEFENDER
    assert op.archetype == RoleArchetype.DEF_PROTECTOR
    assert op.attack_type == AttackType.PHYSICAL


def test_cairn_no_skill():
    op = make_cairn()
    assert op.skill is None
