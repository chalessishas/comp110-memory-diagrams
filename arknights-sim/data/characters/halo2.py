"""Halo Alter (溯光星源) — 6★ Supporter (char_1047).

S1: sp_cost=6, initial_sp=0, instant, AUTO_ATTACK, AUTO (stub).
S2: sp_cost=40, initial_sp=20, duration=30s, AUTO_TIME, MANUAL (stub).
S3: sp_cost=70, initial_sp=35, duration=30s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.halo2 import make_halo2 as _base_stats

SUP_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 4) for dy in range(-2, 3)
))

_S1_TAG = "halo2_s1"
_S1_DURATION = 0.0

_S2_TAG = "halo2_s2"
_S2_DURATION = 30.0

_S3_TAG = "halo2_s3"
_S3_DURATION = 30.0


def make_halo2(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Halo Alter"
    op.archetype = RoleArchetype.SUP_BARD
    op.profession = Profession.SUPPORTER
    op.attack_type = AttackType.ARTS
    op.range_shape = SUP_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Halo Alter S1", slot="S1", sp_cost=6, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Halo Alter S2", slot="S2", sp_cost=40, initial_sp=20,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Halo Alter S3", slot="S3", sp_cost=70, initial_sp=35,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
