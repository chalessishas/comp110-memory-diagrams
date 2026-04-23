"""THRM-EX  — no-skill Specialist unit. Config-only tests."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.types import AttackType, Profession, RoleArchetype
from data.characters.therex import make_therex


def test_therex_config():
    op = make_therex()
    assert op.name == "THRM-EX"
    assert op.profession == Profession.SPECIALIST
    assert op.archetype == RoleArchetype.SPEC_PUSHER
    assert op.attack_type == AttackType.PHYSICAL


def test_therex_no_skill():
    op = make_therex()
    assert op.skill is None
