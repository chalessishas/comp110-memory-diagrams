"""Chiave S1/S2 — both DP-mechanic stubs.

Tests cover:
  - S1 config (name, sp_cost=35, initial_sp=20)
  - S2 slot regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.characters.chiave import make_chiave, _S1_TAG, _S1_DURATION, _S2_TAG


def test_chiave_s1_config():
    op = make_chiave(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Charge γ"
    assert sk.sp_cost == 35
    assert sk.initial_sp == 20
    assert sk.duration == _S1_DURATION
    assert sk.behavior_tag == _S1_TAG


def test_s2_slot_config():
    op = make_chiave(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Blazing Wire Stripper"
    assert sk.behavior_tag == _S2_TAG
