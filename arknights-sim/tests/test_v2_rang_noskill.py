"""Ranger  — no-skill Sniper helper. Config-only tests."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.types import AttackType, Profession, RoleArchetype
from data.characters.rang import make_rang


def test_rang_config():
    op = make_rang()
    assert op.name == "Ranger"
    assert op.profession == Profession.SNIPER
    assert op.archetype == RoleArchetype.SNIPER_MARKSMAN
    assert op.attack_type == AttackType.PHYSICAL


def test_rang_no_skill():
    op = make_rang()
    assert op.skill is None
