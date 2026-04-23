"""Durin — 2★ no-skill Caster. Config-only tests."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.types import AttackType, Profession, RoleArchetype
from data.characters.durin import make_durin


def test_durin_config():
    op = make_durin()
    assert op.name == "Durin"
    assert op.profession == Profession.CASTER
    assert op.archetype == RoleArchetype.CASTER_CORE
    assert op.attack_type == AttackType.ARTS


def test_durin_no_skill():
    op = make_durin()
    assert op.skill is None
