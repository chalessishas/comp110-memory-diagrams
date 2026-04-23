"""12F — 1★ Caster, no skills at E0 max level.

Module name starts with a digit; importlib used for both the character and test import.

Tests cover:
  - Config: name, profession, attack_type
  - Skill is None (no-skill operator)
"""
from __future__ import annotations
import sys, os, importlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

_mod = importlib.import_module('data.characters.12fce')
make_12fce = _mod.make_12fce

from core.types import AttackType, Profession


def test_12fce_config():
    op = make_12fce()
    assert op.name == "12F"
    assert op.profession == Profession.CASTER
    assert op.attack_type == AttackType.ARTS


def test_12fce_no_skill():
    op = make_12fce()
    assert op.skill is None
