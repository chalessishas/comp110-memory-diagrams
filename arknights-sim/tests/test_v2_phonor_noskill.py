"""PhonoR-0  — no-skill Supporter robot. Config-only tests."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.types import AttackType, Profession, RoleArchetype
from data.characters.phonor import make_phonor


def test_phonor_config():
    op = make_phonor()
    assert op.name == "PhonoR-0"
    assert op.profession == Profession.SUPPORTER
    assert op.archetype == RoleArchetype.SUP_DECEL
    assert op.attack_type == AttackType.ARTS


def test_phonor_no_skill():
    op = make_phonor()
    assert op.skill is None
