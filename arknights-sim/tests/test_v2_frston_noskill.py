"""Friston-3  — no-skill Defender robot. Config-only tests."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.types import AttackType, Profession, RoleArchetype
from data.characters.frston import make_frston


def test_frston_config():
    op = make_frston()
    assert op.name == "Friston-3"
    assert op.profession == Profession.DEFENDER
    assert op.archetype == RoleArchetype.DEF_PROTECTOR
    assert op.attack_type == AttackType.PHYSICAL


def test_frston_no_skill():
    op = make_frston()
    assert op.skill is None
