"""Palico  — no-skill Sniper collab. Config-only tests."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.types import AttackType, Profession, RoleArchetype
from data.characters.palico import make_palico


def test_palico_config():
    op = make_palico()
    assert op.name == "Palico"
    assert op.profession == Profession.SNIPER
    assert op.archetype == RoleArchetype.SNIPER_MARKSMAN
    assert op.attack_type == AttackType.PHYSICAL


def test_palico_no_skill():
    op = make_palico()
    assert op.skill is None
