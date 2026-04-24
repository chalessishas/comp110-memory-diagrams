"""Zuole — 6★ Guard (GUARD_FIGHTER).

S1: sp_cost=8, initial_sp=4, duration=0.0s, AUTO_ATTACK, AUTO (stub).
S2: sp_cost=40, initial_sp=20, duration=20.0s, AUTO_TIME, MANUAL (stub).
S3: sp_cost=65, initial_sp=32, duration=20.0s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.zuole import make_zuole as _base_stats

OP_RANGE = RangeShape(tiles=((0, 0), (1, 0)))
_S1_TAG = "zuole_s1"; _S1_DURATION = 0.0
_S2_TAG = "zuole_s2"; _S2_DURATION = 20.0
_S3_TAG = "zuole_s3"; _S3_DURATION = 20.0

def make_zuole(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Zuole"
    op.archetype = RoleArchetype.GUARD_FIGHTER
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = OP_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Zuole S1", slot="S1", sp_cost=8, initial_sp=4,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Zuole S2", slot="S2", sp_cost=40, initial_sp=20,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    elif slot == "S3":
        op.skill = SkillComponent(name="Zuole S3", slot="S3", sp_cost=65, initial_sp=32,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
