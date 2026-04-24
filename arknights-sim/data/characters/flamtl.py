"""Flametail (焰尾) — 6★ Vanguard (Pioneer).

S1: sp_cost=30, initial_sp=15, duration=15s, AUTO_TIME, MANUAL (stub).
S2: sp_cost=45, initial_sp=20, duration=20s, AUTO_TIME, MANUAL (stub).
S3: sp_cost=55, initial_sp=25, duration=20s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.flamtl import make_flamtl as _base_stats

VAN_RANGE = RangeShape(tiles=((0, 0), (0, -1), (0, 1), (1, 0)))

_S1_TAG = "flamtl_s1"
_S1_DURATION = 15.0

_S2_TAG = "flamtl_s2"
_S2_DURATION = 20.0

_S3_TAG = "flamtl_s3"
_S3_DURATION = 20.0


def make_flamtl(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Flametail"
    op.archetype = RoleArchetype.VAN_PIONEER
    op.profession = Profession.VANGUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = VAN_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Flametail S1", slot="S1", sp_cost=30, initial_sp=15,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Flametail S2", slot="S2", sp_cost=45, initial_sp=20,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Flametail S3", slot="S3", sp_cost=55, initial_sp=25,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
