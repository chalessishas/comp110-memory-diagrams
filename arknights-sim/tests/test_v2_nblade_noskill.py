"""Night Blade  — no-skill Vanguard helper. Config-only tests."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.types import AttackType, Profession, RoleArchetype
from data.characters.nblade import make_nblade


def test_nblade_config():
    op = make_nblade()
    assert op.name == "Night Blade"
    assert op.profession == Profession.VANGUARD
    assert op.archetype == RoleArchetype.VAN_PIONEER
    assert op.attack_type == AttackType.PHYSICAL


def test_nblade_no_skill():
    op = make_nblade()
    assert op.skill is None
