"""Botany — no-skill Supporter. Config-only tests."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.types import AttackType, Profession, RoleArchetype
from data.characters.botany import make_botany


def test_botany_config():
    op = make_botany()
    assert op.name == "Botany"
    assert op.profession == Profession.SUPPORTER
    assert op.archetype == RoleArchetype.SUP_DECEL
    assert op.attack_type == AttackType.ARTS


def test_botany_no_skill():
    op = make_botany()
    assert op.skill is None
