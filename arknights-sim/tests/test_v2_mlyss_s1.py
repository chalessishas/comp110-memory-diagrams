"""Muelsyse (Mlyss) — 6★ VAN_TACTICIAN, S1/S2/S3 config tests."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.types import RoleArchetype
from data.characters.mlyss import make_mlyss, _S1_TAG, _S1_DURATION, _S2_TAG, _S2_DURATION, _S3_TAG, _S3_DURATION


def test_mlyss_archetype():
    op = make_mlyss()
    assert op.archetype == RoleArchetype.VAN_TACTICIAN


def test_mlyss_s1_config():
    op = make_mlyss(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.sp_cost == 32 and sk.initial_sp == 8
    assert sk.duration == _S1_DURATION and sk.behavior_tag == _S1_TAG
    assert sk.sp == 8.0


def test_mlyss_s2_config():
    op = make_mlyss(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.sp_cost == 39 and sk.initial_sp == 15
    assert sk.duration == _S2_DURATION and sk.behavior_tag == _S2_TAG
    assert sk.sp == 15.0


def test_mlyss_s3_config():
    op = make_mlyss(slot="S3")
    sk = op.skill
    assert sk is not None and sk.slot == "S3"
    assert sk.sp_cost == 39 and sk.initial_sp == 15
    assert sk.duration == _S3_DURATION and sk.behavior_tag == _S3_TAG
    assert sk.sp == 15.0
