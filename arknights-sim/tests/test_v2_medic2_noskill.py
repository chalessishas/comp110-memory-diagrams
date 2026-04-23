"""Lancet-2  — no-skill Medic robot. Config-only tests."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.types import AttackType, Profession, RoleArchetype
from data.characters.medic2 import make_medic2


def test_medic2_config():
    op = make_medic2()
    assert op.name == "Lancet-2"
    assert op.profession == Profession.MEDIC
    assert op.archetype == RoleArchetype.MEDIC_ST
    assert op.attack_type == AttackType.HEAL


def test_medic2_no_skill():
    op = make_medic2()
    assert op.skill is None
