"""CONFESS-47 — no-skill Vanguard. Config-only tests."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.types import AttackType, Profession, RoleArchetype
from data.characters.confes import make_confes


def test_confes_config():
    op = make_confes()
    assert op.name == "CONFESS-47"
    assert op.profession == Profession.VANGUARD
    assert op.archetype == RoleArchetype.VAN_PIONEER
    assert op.attack_type == AttackType.PHYSICAL


def test_confes_no_skill():
    op = make_confes()
    assert op.skill is None
