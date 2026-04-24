"""Kafka — 5★ SPEC_EXECUTOR. S1 'Cube of Absurdism' ON_DEPLOY config test."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.types import SPGainMode, SkillTrigger
from data.characters.kafka import make_kafka, _S1_TAG


def test_kafka_s1_config():
    op = make_kafka(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Cube of Absurdism"
    assert sk.sp_cost == 0 and sk.initial_sp == 0
    assert sk.sp_gain_mode == SPGainMode.ON_DEPLOY
    assert sk.trigger == SkillTrigger.AUTO
    assert sk.behavior_tag == _S1_TAG
