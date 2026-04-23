"""Virtuosa S1/S2/S3 — all stub skills. Config tests only.

Tests cover:
  - S3 config (name, sp_cost=60, initial_sp=32, duration=34s)
  - S2 slot regression
  - S1 slot regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.characters.cello import make_cello, _S1_TAG, _S2_TAG, _S2_DURATION, _S3_TAG, _S3_DURATION


def test_cello_s3_config():
    op = make_cello(slot="S3")
    sk = op.skill
    assert sk is not None and sk.slot == "S3"
    assert sk.name == "Liberal Tango"
    assert sk.sp_cost == 60
    assert sk.initial_sp == 32
    assert sk.duration == _S3_DURATION
    assert sk.behavior_tag == _S3_TAG


def test_s2_slot_config():
    op = make_cello(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Requiem Mass"
    assert sk.sp_cost == 30
    assert sk.duration == _S2_DURATION
    assert sk.behavior_tag == _S2_TAG


def test_s1_slot_config():
    op = make_cello(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Golden Ecstasy"
    assert sk.behavior_tag == _S1_TAG
