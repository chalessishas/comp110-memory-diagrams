"""angel — alias for Exusiai (char_103_angel duplicate stem).

Tests cover:
  - make_angel returns operator named Exusiai with S3 skill
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.characters.angel import make_angel


def test_angel_alias_returns_exusiai():
    op = make_angel(slot="S3")
    assert op.name == "Exusiai"
    assert op.skill is not None and op.skill.slot == "S3"
