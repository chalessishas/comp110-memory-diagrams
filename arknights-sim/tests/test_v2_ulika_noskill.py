"""U-Official  — no-skill Supporter robot. Config-only tests."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.types import AttackType, Profession, RoleArchetype
from data.characters.ulika import make_ulika


def test_ulika_config():
    op = make_ulika()
    assert op.name == "U-Official"
    assert op.profession == Profession.SUPPORTER
    assert op.archetype == RoleArchetype.SUP_DECEL
    assert op.attack_type == AttackType.ARTS


def test_ulika_no_skill():
    op = make_ulika()
    assert op.skill is None
