"""Executor the Ex Foedere (excu2) S1/S2/S3 — all stub skills.

Tests cover:
  - S1 config (sp_cost=5, initial_sp=0, AUTO_ATTACK)
  - S2 slot regression
  - S3 slot regression (default)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.characters.excu2 import make_excu2, _S1_TAG, _S1_DURATION, _S2_TAG, _S3_TAG


def test_excu2_s1_config():
    op = make_excu2(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.sp_cost == 5
    assert sk.initial_sp == 0
    assert sk.duration == _S1_DURATION
    assert sk.behavior_tag == _S1_TAG


def test_s2_slot_config():
    op = make_excu2(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.behavior_tag == _S2_TAG


def test_s3_slot_config():
    op = make_excu2(slot="S3")
    sk = op.skill
    assert sk is not None and sk.slot == "S3"
    assert sk.behavior_tag == _S3_TAG
