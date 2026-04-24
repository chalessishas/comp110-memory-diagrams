"""Saria (demkni) S1/S2/S3 — all stub skills.

Tests cover:
  - S1 config (name, sp_cost=4, initial_sp=0)
  - S2 slot regression
  - S3 slot regression (default)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.characters.demkni import make_demkni, _S1_TAG, _S1_DURATION, _S2_TAG, _S3_TAG


def test_demkni_s1_config():
    op = make_demkni(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Brilliant Concept"
    assert sk.sp_cost == 4
    assert sk.initial_sp == 0
    assert sk.duration == _S1_DURATION
    assert sk.behavior_tag == _S1_TAG


def test_s2_slot_config():
    op = make_demkni(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Calcification"
    assert sk.behavior_tag == _S2_TAG


def test_s3_slot_config():
    op = make_demkni(slot="S3")
    sk = op.skill
    assert sk is not None and sk.slot == "S3"
    assert sk.name == "The Last Stand"
    assert sk.behavior_tag == _S3_TAG
