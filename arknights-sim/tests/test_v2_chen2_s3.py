"""Ch'en HD S1/S2/S3 — all ammo-based stub skills. Config tests only.

Tests cover:
  - S3 config (name, sp_cost=60, initial_sp=25)
  - S2 slot regression
  - S1 slot regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.characters.chen2 import make_chen2, _S1_TAG, _S2_TAG, _S3_TAG


def test_chen2_s3_config():
    op = make_chen2(slot="S3")
    sk = op.skill
    assert sk is not None and sk.slot == "S3"
    assert sk.name == "Holiday Storm"
    assert sk.sp_cost == 60
    assert sk.initial_sp == 25
    assert sk.behavior_tag == _S3_TAG


def test_s2_slot_config():
    op = make_chen2(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Night of Violet"
    assert sk.sp_cost == 24
    assert sk.behavior_tag == _S2_TAG


def test_s1_slot_config():
    op = make_chen2(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "High-Pressure Splash"
    assert sk.behavior_tag == _S1_TAG
