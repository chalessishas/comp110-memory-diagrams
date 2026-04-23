"""Castle-3 — no-skill Guard drone. Config-only tests."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.types import AttackType, Profession, RoleArchetype
from data.characters.cast3 import make_cast3


def test_cast3_config():
    op = make_cast3()
    assert op.name == "Castle-3"
    assert op.profession == Profession.GUARD
    assert op.archetype == RoleArchetype.GUARD_FIGHTER
    assert op.attack_type == AttackType.PHYSICAL


def test_cast3_no_skill():
    op = make_cast3()
    assert op.skill is None
