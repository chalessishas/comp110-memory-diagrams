"""Justice Knight  — no-skill Sniper robot. Config-only tests."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.types import AttackType, Profession, RoleArchetype
from data.characters.jnight import make_jnight


def test_jnight_config():
    op = make_jnight()
    assert op.name == "Justice Knight"
    assert op.profession == Profession.SNIPER
    assert op.archetype == RoleArchetype.SNIPER_MARKSMAN
    assert op.attack_type == AttackType.PHYSICAL


def test_jnight_no_skill():
    op = make_jnight()
    assert op.skill is None
