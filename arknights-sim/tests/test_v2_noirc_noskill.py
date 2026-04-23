"""Noir Corne  — no-skill Defender helper. Config-only tests."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.types import AttackType, Profession, RoleArchetype
from data.characters.noirc import make_noirc


def test_noirc_config():
    op = make_noirc()
    assert op.name == "Noir Corne"
    assert op.profession == Profession.DEFENDER
    assert op.archetype == RoleArchetype.DEF_PROTECTOR
    assert op.attack_type == AttackType.PHYSICAL


def test_noirc_no_skill():
    op = make_noirc()
    assert op.skill is None
