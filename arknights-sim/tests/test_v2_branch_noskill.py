"""Branch — no-skill Defender. Config-only tests."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.types import AttackType, Profession, RoleArchetype
from data.characters.branch import make_branch


def test_branch_config():
    op = make_branch()
    assert op.name == "Branch"
    assert op.profession == Profession.DEFENDER
    assert op.archetype == RoleArchetype.DEF_PROTECTOR
    assert op.attack_type == AttackType.PHYSICAL


def test_branch_no_skill():
    op = make_branch()
    assert op.skill is None
